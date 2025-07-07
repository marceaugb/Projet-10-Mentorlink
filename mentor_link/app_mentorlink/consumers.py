from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
import json
from django.contrib.auth import get_user_model
from .models import Room, Message, MessageReadStatus

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_slug = self.scope['url_route']['kwargs']['room_slug']
        self.room_group_name = f'chat_{self.room_slug}'
        user = self.scope["user"]
        
        if user.is_authenticated:
            room_exists = await self.check_user_in_room(user, self.room_slug)
            if room_exists:
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.accept()
                
                # Envoyer les messages non lus à la connexion
                await self.send_unread_messages(user, self.room_slug)
                
                print(f"WebSocket connecté pour room_slug: {self.room_slug}, user: {user.username}")
            else:
                await self.close()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            print(f"Données reçues: {text_data_json}")
            
            # Si c'est une demande de marquage comme lu
            if text_data_json.get('type') == 'mark_as_read':
                await self.mark_messages_as_read(self.scope["user"], self.room_slug)
                return
            
            message_content = text_data_json.get('message', '').strip()
            user = self.scope["user"]

            if user.is_authenticated and message_content:
                # Sauvegarder le message (UN SEUL APPEL)
                message = await self.save_message(user, self.room_slug, message_content)
                print(f"Message sauvegardé: {message}")
                
                if message:
                    # Envoyer à tous les membres du groupe
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': message_content,
                            'username': user.username,
                            'user_id': user.id,
                            'timestamp': message['timestamp'],
                            'message_id': message['id']
                        }
                    )
                    
                    # Notifier les autres utilisateurs
                    await self.notify_other_users(user, self.room_slug)
                    
        except json.JSONDecodeError:
            print("Erreur: Format JSON invalide")
        except Exception as e:
            print(f"Erreur dans receive: {e}")

    async def send_unread_messages(self, user, room_slug):
        """Envoyer tous les messages non lus à l'utilisateur qui se connecte"""
        try:
            unread_messages = await self.get_unread_messages(user, room_slug)
            
            for message in unread_messages:
                await self.send(text_data=json.dumps({
                    'type': 'unread_message',
                    'message': message['content'],
                    'username': message['username'],
                    'user_id': message['user_id'],
                    'timestamp': message['timestamp'],
                    'message_id': message['id']
                }))
                
            # Marquer automatiquement comme lus après envoi
            if unread_messages:
                await self.mark_messages_as_read(user, room_slug)
                
        except Exception as e:
            print(f"Erreur send_unread_messages: {e}")

    # ========== MÉTHODES UTILITAIRES ==========

    @database_sync_to_async
    def get_unread_messages(self, user, room_slug):
        """Récupérer les messages non lus pour cet utilisateur dans cette room"""
        try:
            room = Room.objects.get(slug=room_slug)
            unread_messages = Message.objects.filter(
                room=room
            ).exclude(user=user).exclude(
                id__in=MessageReadStatus.objects.filter(user=user).values_list('message_id', flat=True)
            ).order_by('timestamp')
            
            return [{
                'id': msg.id,
                'content': msg.content,
                'username': msg.user.username,
                'timestamp': msg.timestamp.strftime('%d/%m/%Y %H:%M:%S'),
                'user_id': msg.user.id
            } for msg in unread_messages]
        except Room.DoesNotExist:
            return []

    @database_sync_to_async
    def check_user_in_room(self, user, room_slug):
        """Vérifier que l'utilisateur fait partie de cette room"""
        try:
            room = Room.objects.get(slug=room_slug)
            return room.users.filter(id=user.id).exists()
        except Room.DoesNotExist:
            return False

    async def chat_message(self, event):
        """Envoyer le message au client WebSocket avec données utilisateur complètes"""
        try:
            await self.send(text_data=json.dumps({
                'type': 'chat_message',
                'message': event['message'],
                'user': event.get('username', 'Utilisateur inconnu'),  # ✅ Valeur par défaut
                'username': event.get('username', 'Utilisateur inconnu'),
                'user_id': event.get('user_id', 0),
                'timestamp': event.get('timestamp', ''),
                'message_id': event.get('message_id', 0)
            }))
        except Exception as e:
            print(f"Erreur lors de l'envoi du message: {e}")

    @database_sync_to_async
    def save_message(self, user, room_slug, content):
        """Sauvegarder un message avec données utilisateur complètes"""
        try:
            room = Room.objects.get(slug=room_slug)
            message = Message.objects.create(
                user=user,
                room=room,
                content=content
            )
            
            # ✅ S'assurer que toutes les données utilisateur sont présentes
            user_data = {
                'id': message.id,
                'content': message.content,
                'timestamp': message.timestamp.strftime('%d/%m/%Y %H:%M:%S'),
                'user_id': user.id if user else 0,
                'username': user.username if user and hasattr(user, 'username') else 'Utilisateur inconnu',
                'first_name': user.first_name if user and hasattr(user, 'first_name') else '',
                'last_name': user.last_name if user and hasattr(user, 'last_name') else ''
            }
            
            return user_data
            
        except Exception as e:
            print(f"Erreur sauvegarde message: {e}")
            return None


    @database_sync_to_async
    def get_room_users(self, room_slug):
        """Récupérer tous les utilisateurs d'une room"""
        try:
            room = Room.objects.get(slug=room_slug)
            return list(room.users.all())
        except Room.DoesNotExist:
            return []

    @database_sync_to_async
    def get_unread_count_for_user(self, user):
        """Compter les messages non lus pour un utilisateur"""
        try:
            unread_count = Message.objects.filter(
                room__users=user
            ).exclude(
                user=user
            ).exclude(
                id__in=MessageReadStatus.objects.filter(user=user).values_list('message_id', flat=True)
            ).count()
            return unread_count
        except Exception as e:
            print(f"Erreur get_unread_count_for_user: {e}")
            return 0

    async def notify_other_users(self, sender, room_slug):
        """Notifier les autres utilisateurs qu'il y a un nouveau message"""
        try:
            room_users = await self.get_room_users(room_slug)
            
            for user in room_users:
                if user != sender:
                    unread_count = await self.get_unread_count_for_user(user)
                    
                    # Envoyer notification via WebSocket de notification global
                    await self.channel_layer.group_send(
                        f"user_{user.id}_notifications",
                        {
                            'type': 'send_notification',
                            'unread_count': unread_count,
                            'message': f'Nouveau message de {sender.username}',
                            'room_slug': room_slug
                        }
                    )
        except Exception as e:
            print(f"Erreur notify_other_users: {e}")

    @database_sync_to_async
    def mark_messages_as_read(self, user, room_slug):
        """Marquer tous les messages de cette room comme lus pour cet utilisateur"""
        try:
            room = Room.objects.get(slug=room_slug)
            messages_to_mark = Message.objects.filter(room=room).exclude(user=user)
            
            for message in messages_to_mark:
                MessageReadStatus.objects.get_or_create(
                    message=message,
                    user=user
                )
            return True
        except Room.DoesNotExist:
            return False
        except Exception as e:
            print(f"Erreur mark_messages_as_read: {e}")
            return False


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.group_name = f"user_{self.user.id}_notifications"
            
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'unread_count_update',
            'unread_count': event['unread_count']
        }))
