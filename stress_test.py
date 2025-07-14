#!/usr/bin/env python3
"""
Testeur de charge pour valider l'autoscaling Django
Créé pour tester notre setup Docker avec NGINX qui redémarre tout le temps...

Usage rapide:
    python stress_test.py

Ce que ça fait:
    - Détecte quand NGINX plante (502/504, connexions qui tombent)
    - Met en pause automatiquement et reprend quand c'est bon
    - Affiche les stats importantes en temps réel
    - Monte la charge progressivement comme on veut
    - Marche bien avec asyncio (testé en prod)

Installation:
    pip install aiohttp click rich

Pour CI/CD:
    Codes de retour:
    - 0: tout s'est bien passé
    - 1: service down trop longtemps
    - 2: problème de config
"""

import asyncio
import time
import statistics
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import signal
import sys

import aiohttp
import click
from rich.console import Console
from rich.table import Table
from rich.live import Live


class PhaseTest(Enum):
    MONTEE = "montée"
    PLATEAU = "plateau"  
    DESCENTE = "descente"
    PAUSE = "pause"
    REPOS = "repos"
    FINI = "fini"


@dataclass
class ReponseHttp:
    code_status: int
    temps_reponse: float
    erreur: Optional[str] = None


@dataclass
class Stats:
    nb_requetes: int = 0
    nb_succes: int = 0
    nb_echecs: int = 0
    temps_reponses: List[float] = field(default_factory=list)
    erreurs: Dict[str, int] = field(default_factory=dict)
    
    @property
    def pourcentage_succes(self) -> float:
        if self.nb_requetes == 0:
            return 0.0
        return (self.nb_succes / self.nb_requetes) * 100


class TesteurDeCharge:
    def __init__(self, url: str, rps_max: int, palier: int, duree_plateau: int, 
                 duree_repos: int, timeout_req: int, timeout_recovery: int):
        self.url = url
        self.rps_max = rps_max
        self.palier = palier
        self.duree_plateau = duree_plateau
        self.duree_repos = duree_repos
        self.timeout_req = timeout_req
        self.timeout_recovery = timeout_recovery
        
        self.stats = Stats()
        self.phase_actuelle = PhaseTest.MONTEE
        self.rps_cible = 0
        self.workers = []
        self.session_http = None
        self.console = Console()
        self.en_marche = True
        self.en_pause = False
        
        # Pour Prometheus si on en a besoin plus tard
        self.metriques_prometheus = {
            'total_requests': 0,
            'failed_requests': 0,
            'current_rps': 0.0
        }

    async def init_session_http(self) -> aiohttp.ClientSession:
        """Créer la session HTTP avec les bons timeouts"""
        timeout = aiohttp.ClientTimeout(total=self.timeout_req)
        # On limite les connexions pour pas surcharger
        connector = aiohttp.TCPConnector(limit=1000, limit_per_host=100)
        return aiohttp.ClientSession(timeout=timeout, connector=connector)

    async def envoyer_requete(self) -> ReponseHttp:
        """Envoie une requête HTTP et gère les erreurs"""
        debut = time.time()
        try:
            async with self.session_http.get(self.url) as resp:
                await resp.read()  # On lit tout pour être sûr
                duree = time.time() - debut
                return ReponseHttp(
                    code_status=resp.status,
                    temps_reponse=duree
                )
        except asyncio.TimeoutError:
            return ReponseHttp(
                code_status=0,
                temps_reponse=time.time() - debut,
                erreur="timeout"
            )
        except aiohttp.ClientConnectorError:
            return ReponseHttp(
                code_status=0,
                temps_reponse=time.time() - debut,
                erreur="connexion_fermee"
            )
        except Exception as e:
            return ReponseHttp(
                code_status=0,
                temps_reponse=time.time() - debut,
                erreur=str(e)
            )

    def detecter_restart_nginx(self, reponse: ReponseHttp) -> bool:
        """Détecte si NGINX vient de redémarrer (notre problème principal)"""
        # Les codes d'erreur typiques quand NGINX redémarre
        if reponse.code_status in [502, 504]:
            return True
        # Connexions qui tombent = souvent un restart
        if reponse.erreur in ["connexion_fermee", "timeout"]:
            return True
        return False

    async def verifier_si_up(self) -> bool:
        """Vérifie rapidement si le service répond"""
        try:
            async with self.session_http.get(self.url) as resp:
                return resp.status == 200
        except:
            return False

    async def attendre_que_ca_remarche(self) -> bool:
        """Attend que le service revienne après un restart NGINX"""
        self.console.print("[yellow]NGINX a redémarré, on attend que ça revienne...[/yellow]")
        
        debut_attente = time.time()
        while time.time() - debut_attente < self.timeout_recovery:
            if await self.verifier_si_up():
                self.console.print("[green]C'est reparti, on reprend![/green]")
                return True
            await asyncio.sleep(1)  # On vérifie toutes les secondes
        
        self.console.print(f"[red]Toujours pas revenu après {self.timeout_recovery}s, on abandonne[/red]")
        return False

    async def worker_requetes(self, id_worker: int):
        """Un worker qui envoie des requêtes en continu"""
        while self.en_marche:
            if self.en_pause:
                await asyncio.sleep(0.1)
                continue
                
            # On calcule le délai entre requêtes selon le RPS voulu
            if self.rps_cible > 0:
                delai = len(self.workers) / self.rps_cible
                await asyncio.sleep(delai)
            else:
                await asyncio.sleep(1)
                continue
            
            reponse = await self.envoyer_requete()
            
            # On met à jour nos stats
            self.stats.nb_requetes += 1
            self.stats.temps_reponses.append(reponse.temps_reponse)
            
            if reponse.code_status == 200:
                self.stats.nb_succes += 1
            else:
                self.stats.nb_echecs += 1
                if reponse.erreur:
                    self.stats.erreurs[reponse.erreur] = self.stats.erreurs.get(reponse.erreur, 0) + 1
                else:
                    cle_erreur = f"http_{reponse.code_status}"
                    self.stats.erreurs[cle_erreur] = self.stats.erreurs.get(cle_erreur, 0) + 1
            
            # Si on détecte un restart NGINX, on met tout en pause
            if self.detecter_restart_nginx(reponse):
                self.en_pause = True
                if not await self.attendre_que_ca_remarche():
                    self.en_marche = False
                    sys.exit(1)
                self.en_pause = False

    async def gerer_workers(self, nb_workers_voulu: int):
        """Ajuste le nombre de workers selon le RPS voulu"""
        nb_workers_actuel = len(self.workers)
        
        if nb_workers_voulu > nb_workers_actuel:
            # On ajoute des workers
            for i in range(nb_workers_voulu - nb_workers_actuel):
                worker = asyncio.create_task(self.worker_requetes(nb_workers_actuel + i))
                self.workers.append(worker)
        elif nb_workers_voulu < nb_workers_actuel:
            # On en supprime
            for _ in range(nb_workers_actuel - nb_workers_voulu):
                if self.workers:
                    worker = self.workers.pop()
                    worker.cancel()
                    try:
                        await worker
                    except asyncio.CancelledError:
                        pass

    def creer_affichage(self) -> Table:
        """Crée l'affichage temps réel (version simplifiée comme demandé)"""
        tableau = Table(title="Test de Charge en Cours")
        tableau.add_column("Métrique", style="cyan")
        tableau.add_column("Valeur", style="magenta")
        
        # On affiche la phase actuelle de façon plus lisible
        phase_lisible = self.phase_actuelle.value.capitalize()
        
        tableau.add_row("État", phase_lisible)
        tableau.add_row("Requêtes Totales", f"{self.stats.nb_requetes}")
        tableau.add_row("Taux de Succès", f"{self.stats.pourcentage_succes:.1f}%")
        
        return tableau

    async def lancer_test(self):
        """Boucle principale du test de charge"""
        self.session_http = await self.init_session_http()
        
        try:
            heure_debut = time.time()
            debut_phase = heure_debut
            
            with Live(self.creer_affichage(), refresh_per_second=2) as affichage_live:
                while self.en_marche and self.phase_actuelle != PhaseTest.FINI:
                    maintenant = time.time()
                    duree_phase = maintenant - debut_phase
                    
                    # Gestion des différentes phases du test
                    if self.phase_actuelle == PhaseTest.MONTEE:
                        if self.rps_cible < self.rps_max:
                            self.rps_cible = min(self.rps_cible + self.palier, self.rps_max)
                            await self.gerer_workers(self.rps_cible)
                        else:
                            self.phase_actuelle = PhaseTest.PLATEAU
                            debut_phase = maintenant
                    
                    elif self.phase_actuelle == PhaseTest.PLATEAU:
                        if duree_phase >= self.duree_plateau:
                            self.phase_actuelle = PhaseTest.DESCENTE
                            debut_phase = maintenant
                    
                    elif self.phase_actuelle == PhaseTest.DESCENTE:
                        if self.rps_cible > 0:
                            self.rps_cible = max(self.rps_cible - self.palier, 0)
                            await self.gerer_workers(self.rps_cible)
                        else:
                            self.phase_actuelle = PhaseTest.REPOS
                            debut_phase = maintenant
                    
                    elif self.phase_actuelle == PhaseTest.REPOS:
                        if duree_phase >= self.duree_repos:
                            self.phase_actuelle = PhaseTest.FINI
                    
                    # On met à jour l'affichage
                    affichage_live.update(self.creer_affichage())
                    
                    await asyncio.sleep(1)
        
        finally:
            # Nettoyage à la fin
            for worker in self.workers:
                worker.cancel()
            await asyncio.gather(*self.workers, return_exceptions=True)
            await self.session_http.close()

    def exporter_pour_prometheus(self) -> str:
        """Export des métriques pour Prometheus (au cas où)"""
        metriques = []
        metriques.append(f"test_charge_requetes_total {self.stats.nb_requetes}")
        metriques.append(f"test_charge_echecs_total {self.stats.nb_echecs}")
        metriques.append(f"test_charge_taux_succes {self.stats.pourcentage_succes}")
        return "\n".join(metriques)


@click.command()
@click.option('--url', default='http://localhost/', help='URL à tester')
@click.option('--step', default=50, help='Palier de montée en RPS')
@click.option('--max', 'rps_max', default=400, help='RPS maximum à atteindre')
@click.option('--hold', default=60, help='Temps de maintien au max (secondes)')
@click.option('--cooldown', default=120, help='Temps de repos final (secondes)')
@click.option('--timeout', default=30, help='Timeout des requêtes (secondes)')
@click.option('--recovery-timeout', default=60, help='Temps d\'attente après restart NGINX (secondes)')
@click.option('--prometheus-output', help='Fichier pour export Prometheus')
def main(url: str, step: int, rps_max: int, hold: int, cooldown: int, 
         timeout: int, recovery_timeout: int, prometheus_output: Optional[str]):
    """
    Testeur de charge pour notre setup Django avec autoscaling
    
    Utilisation simple:
        python stress_test.py
        
    Avec options personnalisées:
        python stress_test.py --url http://localhost:8000 --max 200 --step 25
    """
    
    def arreter_proprement(signum, frame):
        print("\nArrêt du test...")
        sys.exit(0)
    
    # Gestion propre des signaux
    signal.signal(signal.SIGINT, arreter_proprement)
    signal.signal(signal.SIGTERM, arreter_proprement)
    
    testeur = TesteurDeCharge(
        url=url,
        rps_max=rps_max,
        palier=step,
        duree_plateau=hold,
        duree_repos=cooldown,
        timeout_req=timeout,
        timeout_recovery=recovery_timeout
    )
    
    console = Console()
    console.print(f"[green]Démarrage du test sur {url}[/green]")
    console.print(f"[blue]Config: paliers de {step} RPS jusqu'à {rps_max} RPS, plateau {hold}s, repos {cooldown}s[/blue]")
    
    try:
        asyncio.run(testeur.lancer_test())
        
        # Export Prometheus si demandé
        if prometheus_output:
            with open(prometheus_output, 'w') as f:
                f.write(testeur.exporter_pour_prometheus())
            console.print(f"[green]Métriques sauvées dans {prometheus_output}[/green]")
        
        # Résumé final
        console.print("\n[green]Test terminé avec succès![/green]")
        console.print(f"Total requêtes: {testeur.stats.nb_requetes}")
        console.print(f"Taux de succès: {testeur.stats.pourcentage_succes:.1f}%")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrompu[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Erreur: {e}[/red]")
        sys.exit(2)


if __name__ == "__main__":
    main()
