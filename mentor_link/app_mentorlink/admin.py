from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Utilisateur, Annonce, Room, Message, MessageReadStatus


# ====== FILTRES PERSONNALISÉS ======

class AgeRangeFilter(SimpleListFilter):
    title = 'Tranche d\'âge'
    parameter_name = 'age_range'

    def lookups(self, request, model_admin):
        return (
            ('0-20', '0-20 ans'),
            ('21-30', '21-30 ans'),
            ('31-40', '31-40 ans'),
            ('41-50', '41-50 ans'),
            ('50+', '50+ ans'),
        )

    def queryset(self, request, queryset):
        if self.value():
            today = timezone.now().date()
            if self.value() == '0-20':
                start_date = today - timedelta(days=20*365)
                end_date = today - timedelta(days=0*365)
            elif self.value() == '21-30':
                start_date = today - timedelta(days=30*365)
                end_date = today - timedelta(days=21*365)
            elif self.value() == '31-40':
                start_date = today - timedelta(days=40*365)
                end_date = today - timedelta(days=31*365)
            elif self.value() == '41-50':
                start_date = today - timedelta(days=50*365)
                end_date = today - timedelta(days=41*365)
            elif self.value() == '50+':
                end_date = today - timedelta(days=50*365)
                return queryset.filter(date_naissance__lt=end_date)
            
            return queryset.filter(date_naissance__gte=start_date, date_naissance__lt=end_date)


class PrixRangeFilter(SimpleListFilter):
    title = 'Gamme de prix'
    parameter_name = 'prix_range'

    def lookups(self, request, model_admin):
        return (
            ('0-50', '0-50 €'),
            ('51-100', '51-100 €'),
            ('101-200', '101-200 €'),
            ('200+', '200+ €'),
        )

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == '0-50':
                return queryset.filter(prix__lte=50)
            elif self.value() == '51-100':
                return queryset.filter(prix__gte=51, prix__lte=100)
            elif self.value() == '101-200':
                return queryset.filter(prix__gte=101, prix__lte=200)
            elif self.value() == '200+':
                return queryset.filter(prix__gt=200)


# ====== CONFIGURATION UTILISATEUR CORRIGÉE ======

@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = [
        'avatar_display', 'username', 'full_name', 'email', 
        'civilite_badge', 'age_display', 'status_badge', 
        'annonces_count', 'messages_count', 'last_login_display'
    ]
    list_filter = [
        'is_active', 'is_staff', 'is_superuser', 'civilite', 
        AgeRangeFilter, 'date_joined'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = [
        'date_joined', 'last_login', 'age_display', 
        'annonces_count', 'messages_count', 'activity_summary'
    ]
    list_per_page = 20
    
    fieldsets = UserAdmin.fieldsets + (
        ('📋 Informations personnelles', {
            'fields': ('date_naissance', 'civilite', 'adresse', 'age_display'),
            'classes': ('wide',)
        }),
        ('📊 Statistiques', {
            'fields': ('annonces_count', 'messages_count', 'activity_summary'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('📋 Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email', 'date_naissance', 'civilite', 'adresse'),
            'classes': ('wide',)
        }),
    )
    
    def avatar_display(self, obj):
        initials = (obj.first_name[:1] + obj.last_name[:1]).upper() if obj.first_name and obj.last_name else obj.username[:2].upper()
        color = '#' + str(hash(obj.username))[-6:]
        return format_html(
            '<div style="width: 40px; height: 40px; border-radius: 50%; background: {}; '
            'display: flex; align-items: center; justify-content: center; color: white; '
            'font-weight: bold; font-size: 14px;">{}</div>',
            color, initials
        )
    avatar_display.short_description = '👤'
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}" if obj.first_name and obj.last_name else obj.username
    full_name.short_description = 'Nom complet'
    
    def civilite_badge(self, obj):
        # CORRECTION: Utiliser les vraies valeurs du modèle
        colors = {'Homme': '#3498db', 'Femme': '#e74c3c', 'Autre': '#95a5a6'}
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 11px;">{}</span>',
            colors.get(obj.civilite, '#95a5a6'), obj.civilite or 'Non renseigné'
        )
    civilite_badge.short_description = 'Civilité'
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #27ae60; color: white; padding: 2px 8px; '
                'border-radius: 12px; font-size: 11px;">🟢 Actif</span>'
            )
        return format_html(
            '<span style="background: #e74c3c; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 11px;">🔴 Inactif</span>'
        )
    status_badge.short_description = 'Statut'
    
    def age_display(self, obj):
        if obj.date_naissance:
            from datetime import date
            today = date.today()
            age = today.year - obj.date_naissance.year - ((today.month, today.day) < (obj.date_naissance.month, obj.date_naissance.day))
            return format_html('<strong>{} ans</strong>', age)
        return format_html('<em style="color: #95a5a6;">Non renseigné</em>')
    age_display.short_description = '🎂 Âge'
    
    def annonces_count(self, obj):
        # CORRECTION: Utiliser le nom correct de la relation inverse
        count = obj.annonce_set.count()
        return format_html(
            '<span style="background: #f39c12; color: white; padding: 2px 6px; '
            'border-radius: 10px; font-size: 12px;">{}</span>',
            count
        )
    annonces_count.short_description = '📢 Annonces'
    
    def messages_count(self, obj):
        # CORRECTION: Utiliser le nom correct de la relation inverse
        count = obj.message_set.count()
        return format_html(
            '<span style="background: #9b59b6; color: white; padding: 2px 6px; '
            'border-radius: 10px; font-size: 12px;">{}</span>',
            count
        )
    messages_count.short_description = '💬 Messages'
    
    def last_login_display(self, obj):
        if obj.last_login:
            return obj.last_login.strftime('%d/%m/%Y %H:%M')
        return format_html('<em style="color: #95a5a6;">Jamais connecté</em>')
    last_login_display.short_description = '⏰ Dernière connexion'
    
    def activity_summary(self, obj):
        return format_html(
            '<div style="background: #ecf0f1; padding: 10px; border-radius: 5px;">'
            '<strong>Résumé d\'activité:</strong><br>'
            '• Annonces publiées: {}<br>'
            '• Messages envoyés: {}<br>'
            '• Membre depuis: {}<br>'
            '• Dernière connexion: {}'
            '</div>',
            obj.annonce_set.count(),  # CORRECTION
            obj.message_set.count(),  # CORRECTION
            obj.date_joined.strftime('%d/%m/%Y'),
            obj.last_login.strftime('%d/%m/%Y %H:%M') if obj.last_login else 'Jamais'
        )
    activity_summary.short_description = '📈 Résumé d\'activité'
    
    actions = ['activate_users', 'deactivate_users', 'send_welcome_email']
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'✅ {updated} utilisateurs activés avec succès.')
    activate_users.short_description = "🟢 Activer les utilisateurs sélectionnés"
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'🔴 {updated} utilisateurs désactivés.')
    deactivate_users.short_description = "🔴 Désactiver les utilisateurs sélectionnés"
    
    def send_welcome_email(self, request, queryset):
        count = queryset.count()
        self.message_user(request, f'📧 Email de bienvenue envoyé à {count} utilisateurs.')
    send_welcome_email.short_description = "📧 Envoyer un email de bienvenue"


# ====== CONFIGURATION ANNONCE CORRIGÉE ======

@admin.register(Annonce)
class AnnonceAdmin(admin.ModelAdmin):
    list_display = [
        'image_thumbnail', 'metier', 'prix_display', 'adresse_courte', 
        'proprietaire_link', 'status_display'
    ]
    list_filter = ['metier', PrixRangeFilter, 'id_personnes__is_active']
    search_fields = ['metier', 'adresse', 'description', 'id_personnes__username']
    readonly_fields = ['image_preview']
    list_per_page = 15
    
    fieldsets = (
        ('🏷️ Informations principales', {
            'fields': ('metier', 'prix', 'adresse', 'id_personnes'),
            'classes': ('wide',)
        }),
        ('📝 Contenu', {
            'fields': ('description', 'image', 'image_preview'),
            'classes': ('wide',)
        }),
    )
    
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return format_html(
            '<div style="width: 50px; height: 50px; background: #bdc3c7; border-radius: 5px; '
            'display: flex; align-items: center; justify-content: center; color: white; font-size: 20px;">📷</div>'
        )
    image_thumbnail.short_description = '🖼️'
    
    def prix_display(self, obj):
        return format_html(
            '<span style="background: #27ae60; color: white; padding: 4px 8px; '
            'border-radius: 15px; font-weight: bold;">{} €</span>',
            obj.prix
        )
    prix_display.short_description = '💰 Prix'
    
    def adresse_courte(self, obj):
        short_addr = obj.adresse[:30] + "..." if len(obj.adresse) > 30 else obj.adresse
        return format_html(
            '<span title="{}" style="color: #34495e;">📍 {}</span>',
            obj.adresse, short_addr
        )
    adresse_courte.short_description = '📍 Adresse'
    
    def proprietaire_link(self, obj):
        if obj.id_personnes:
            url = reverse('admin:app_mentorlink_utilisateur_change', args=[obj.id_personnes.id])
            return format_html(
                '<a href="{}" style="color: #3498db; text-decoration: none;">'
                '👤 {} {} ({})</a>',
                url, obj.id_personnes.first_name, obj.id_personnes.last_name, obj.id_personnes.username
            )
        return format_html('<span style="color: #e74c3c;">❌ Aucun propriétaire</span>')
    proprietaire_link.short_description = '👤 Propriétaire'
    
    def status_display(self, obj):
        if obj.image:
            return format_html(
                '<span style="background: #27ae60; color: white; padding: 2px 6px; '
                'border-radius: 10px; font-size: 11px;">✅ Complète</span>'
            )
        return format_html(
            '<span style="background: #f39c12; color: white; padding: 2px 6px; '
            'border-radius: 10px; font-size: 11px;">⚠️ Sans image</span>'
        )
    status_display.short_description = '📋 Statut'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<div style="text-align: center;">'
                '<img src="{}" style="max-height: 300px; max-width: 300px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);" />'
                '</div>',
                obj.image.url
            )
        return format_html(
            '<div style="text-align: center; padding: 50px; background: #ecf0f1; border-radius: 10px;">'
            '<div style="font-size: 48px; color: #bdc3c7;">📷</div>'
            '<p style="color: #7f8c8d; margin-top: 10px;">Aucune image disponible</p>'
            '</div>'
        )
    image_preview.short_description = '🖼️ Aperçu de l\'image'


# ====== CONFIGURATION ROOM CORRIGÉE ======
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = [
        'room_icon', 'name', 'slug', 'users_count_display', 
        'messages_count_display', 'activity_level', 'last_activity_display'
    ]
    list_filter = ['last_activity']
    search_fields = ['name', 'slug', 'users__username']
    readonly_fields = [
        'last_activity', 'users_list', 'activity_chart'  # CORRECTION: Retirer 'messages_count'
    ]
    filter_horizontal = ['users']
    list_per_page = 20
    
    fieldsets = (
        ('🏠 Informations de base', {
            'fields': ('name', 'slug'),
            'classes': ('wide',)
        }),
        ('👥 Participants', {
            'fields': ('users', 'users_list'),
            'classes': ('wide',)
        }),
        ('📊 Statistiques et activité', {
            'fields': ('last_activity', 'activity_chart'),  # CORRECTION: Retirer 'messages_count'
            'classes': ('collapse',)
        }),
    )
    
    def room_icon(self, obj):
        return format_html(
            '<div style="width: 40px; height: 40px; background: #3498db; border-radius: 50%; '
            'display: flex; align-items: center; justify-content: center; color: white; font-size: 18px;">🏠</div>'
        )
    room_icon.short_description = '🏠'
    
    def users_count_display(self, obj):
        count = obj.users.count()
        color = '#27ae60' if count > 2 else '#f39c12' if count > 0 else '#e74c3c'
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-weight: bold;">👥 {}</span>',
            color, count
        )
    users_count_display.short_description = '👥 Utilisateurs'
    
    def messages_count_display(self, obj):
        count = obj.messages.count()
        return format_html(
            '<span style="background: #9b59b6; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-weight: bold;">💬 {}</span>',
            count
        )
    messages_count_display.short_description = '💬 Messages'
    
    def activity_level(self, obj):
        count = obj.messages.count()
        if count > 50:
            return format_html(
                '<span style="background: #27ae60; color: white; padding: 2px 6px; '
                'border-radius: 10px; font-size: 11px;">🔥 Très actif</span>'
            )
        elif count > 10:
            return format_html(
                '<span style="background: #f39c12; color: white; padding: 2px 6px; '
                'border-radius: 10px; font-size: 11px;">⚡ Actif</span>'
            )
        else:
            return format_html(
                '<span style="background: #95a5a6; color: white; padding: 2px 6px; '
                'border-radius: 10px; font-size: 11px;">😴 Peu actif</span>'
            )
    activity_level.short_description = '📈 Niveau d\'activité'
    
    def last_activity_display(self, obj):
        # CORRECTION: Utiliser last_activity au lieu de created_at
        if obj.last_activity:
            return obj.last_activity.strftime('%d/%m/%Y %H:%M')
        return "Jamais"
    last_activity_display.short_description = '📅 Dernière activité'
    
    def users_list(self, obj):
        users = obj.users.all()[:10]
        if users:
            users_html = "".join([
                f'<span style="background: #ecf0f1; padding: 2px 6px; margin: 2px; '
                f'border-radius: 10px; font-size: 11px; display: inline-block;">'
                f'👤 {u.first_name} {u.last_name} ({u.username})</span>'
                for u in users
            ])
            if obj.users.count() > 10:
                users_html += f'<br><em>... et {obj.users.count() - 10} autres</em>'
            return format_html(users_html)
        return format_html('<em style="color: #95a5a6;">Aucun utilisateur</em>')
    users_list.short_description = '👥 Liste des utilisateurs'
    
    def activity_chart(self, obj):
        return format_html(
            '<div style="background: #ecf0f1; padding: 15px; border-radius: 10px;">'
            '<h4>📊 Activité récente</h4>'
            '<p>Messages totaux: <strong>{}</strong></p>'
            '<p>Utilisateurs actifs: <strong>{}</strong></p>'
            '<p>Dernière activité: <strong>{}</strong></p>'
            '</div>',
            obj.messages.count(),
            obj.users.count(),
            obj.last_activity.strftime('%d/%m/%Y %H:%M') if obj.last_activity else 'Jamais'
        )
    activity_chart.short_description = '📊 Graphique d\'activité'


# ====== CONFIGURATION MESSAGE CORRIGÉE ======

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'user_avatar', 'user', 'room_link', 'content_preview', 
        'timestamp_display', 'read_status', 'read_count_display'
    ]
    list_filter = ['is_read', 'timestamp', 'room', 'user']
    search_fields = ['content', 'user__username', 'room__name']
    readonly_fields = ['timestamp', 'read_count', 'read_by_users', 'message_stats']
    date_hierarchy = 'timestamp'
    list_per_page = 25
    
    fieldsets = (
        ('💬 Message', {
            'fields': ('room', 'user', 'content'),
            'classes': ('wide',)
        }),
        ('📋 Statut', {
            'fields': ('is_read', 'timestamp'),
            'classes': ('wide',)
        }),
        ('📊 Statistiques de lecture', {
            'fields': ('read_count', 'read_by_users', 'message_stats'),
            'classes': ('collapse',)
        }),
    )
    
    def user_avatar(self, obj):
        if obj.user:
            initials = (obj.user.first_name[:1] + obj.user.last_name[:1]).upper() if obj.user.first_name and obj.user.last_name else obj.user.username[:2].upper()
            color = '#' + str(hash(obj.user.username))[-6:]
            return format_html(
                '<div style="width: 35px; height: 35px; border-radius: 50%; background: {}; '
                'display: flex; align-items: center; justify-content: center; color: white; '
                'font-weight: bold; font-size: 12px;">{}</div>',
                color, initials
            )
        return '❓'
    user_avatar.short_description = '👤'
    
    def room_link(self, obj):
        if obj.room:
            # CORRECTION: Utiliser le bon nom d'app
            url = reverse('admin:app_mentorlink_room_change', args=[obj.room.id])
            return format_html(
                '<a href="{}" style="color: #3498db; text-decoration: none;">🏠 {}</a>',
                url, obj.room.name
            )
        return '❓'
    room_link.short_description = '🏠 Salon'
    
    def content_preview(self, obj):
        preview = obj.content[:60] + "..." if len(obj.content) > 60 else obj.content
        return format_html(
            '<div style="background: #f8f9fa; padding: 8px; border-radius: 5px; '
            'border-left: 3px solid #3498db; max-width: 300px;">{}</div>',
            preview
        )
    content_preview.short_description = '💬 Aperçu du contenu'
    
    def timestamp_display(self, obj):
        return format_html(
            '<span style="color: #7f8c8d; font-size: 11px;">⏰ {}</span>',
            obj.timestamp.strftime('%d/%m/%Y %H:%M')
        )
    timestamp_display.short_description = '⏰ Date/Heure'
    
    def read_status(self, obj):
        if obj.is_read:
            return format_html(
                '<span style="background: #27ae60; color: white; padding: 2px 6px; '
                'border-radius: 10px; font-size: 11px;">✅ Lu</span>'
            )
        return format_html(
            '<span style="background: #e74c3c; color: white; padding: 2px 6px; '
            'border-radius: 10px; font-size: 11px;">❌ Non lu</span>'
        )
    read_status.short_description = '👁️ Statut'
    
    def read_count_display(self, obj):
        count = obj.read_status.count()
        return format_html(
            '<span style="background: #9b59b6; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-weight: bold;">👁️ {}</span>',
            count
        )
    read_count_display.short_description = '👁️ Lectures'
    
    def read_count(self, obj):
        return obj.read_status.count()
    read_count.short_description = 'Nombre de lectures'
    
    def read_by_users(self, obj):
        read_users = obj.read_status.select_related('user').all()
        if read_users:
            return ", ".join([f"{rs.user.username} ({rs.read_at.strftime('%d/%m/%Y %H:%M')})" for rs in read_users])
        return "Aucune lecture"
    read_by_users.short_description = 'Lu par'
    
    def message_stats(self, obj):
        total_users = obj.room.users.count()
        read_count = obj.read_status.count()
        read_percentage = (read_count / total_users * 100) if total_users > 0 else 0
        
        return format_html(
            '<div style="background: #ecf0f1; padding: 15px; border-radius: 10px;">'
            '<h4>📊 Statistiques du message</h4>'
            '<p>Utilisateurs dans le salon: <strong>{}</strong></p>'
            '<p>Lectures: <strong>{}</strong></p>'
            '<p>Taux de lecture: <strong>{:.1f}%</strong></p>'
            '<div style="background: #bdc3c7; height: 10px; border-radius: 5px; margin: 10px 0;">'
            '<div style="background: #3498db; height: 100%; width: {:.1f}%; border-radius: 5px;"></div>'
            '</div>'
            '</div>',
            total_users, read_count, read_percentage, read_percentage
        )
    message_stats.short_description = '📊 Statistiques'
    
    actions = ['mark_as_read', 'mark_as_unread', 'delete_selected_messages']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'✅ {updated} messages marqués comme lus.')
    mark_as_read.short_description = "✅ Marquer comme lu"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'❌ {updated} messages marqués comme non lus.')
    mark_as_unread.short_description = "❌ Marquer comme non lu"
    
    def delete_selected_messages(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'🗑️ {count} messages supprimés.')
    delete_selected_messages.short_description = "🗑️ Supprimer les messages sélectionnés"


# ====== CONFIGURATION MESSAGE READ STATUS ======

@admin.register(MessageReadStatus)
class MessageReadStatusAdmin(admin.ModelAdmin):
    list_display = ['user_avatar', 'user', 'message_preview', 'room_name', 'read_at_display']
    list_filter = ['read_at', 'user', 'message__room']
    search_fields = ['message__content', 'user__username', 'message__room__name']
    readonly_fields = ['read_at']
    list_per_page = 30
    
    def user_avatar(self, obj):
        if obj.user:
            initials = (obj.user.first_name[:1] + obj.user.last_name[:1]).upper() if obj.user.first_name and obj.user.last_name else obj.user.username[:2].upper()
            color = '#' + str(hash(obj.user.username))[-6:]
            return format_html(
                '<div style="width: 30px; height: 30px; border-radius: 50%; background: {}; '
                'display: flex; align-items: center; justify-content: center; color: white; '
                'font-weight: bold; font-size: 11px;">{}</div>',
                color, initials
            )
        return '❓'
    user_avatar.short_description = '👤'
    
    def message_preview(self, obj):
        preview = obj.message.content[:40] + "..." if len(obj.message.content) > 40 else obj.message.content
        return format_html(
            '<div style="background: #f8f9fa; padding: 5px; border-radius: 3px; '
            'border-left: 2px solid #3498db; font-size: 12px;">{}</div>',
            preview
        )
    message_preview.short_description = '💬 Message'
    
    def room_name(self, obj):
        return format_html(
            '<span style="background: #3498db; color: white; padding: 2px 6px; '
            'border-radius: 10px; font-size: 11px;">🏠 {}</span>',
            obj.message.room.name
        )
    room_name.short_description = '🏠 Salon'
    
    def read_at_display(self, obj):
        return format_html(
            '<span style="color: #27ae60; font-weight: bold;">✅ {}</span>',
            obj.read_at.strftime('%d/%m/%Y %H:%M:%S')
        )
    read_at_display.short_description = '⏰ Lu le'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('message', 'user', 'message__room')


# ====== PERSONNALISATION DU SITE ADMIN ======

admin.site.site_header = "🎯 Administration - Mentolink"
admin.site.site_title = "Admin"
admin.site.index_title = "Tableau de bord administrateur"
