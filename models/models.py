from datetime import datetime
import bcrypt
from extensions import db


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    playlists = db.relationship('Playlist', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    history = db.relationship('History', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'avatarUrl': self.avatar_url,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'lastLoginAt': self.last_login_at.isoformat() if self.last_login_at else None,
            'isAuthenticated': True
        }


class Playlist(db.Model):
    __tablename__ = 'playlists'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    cover_art = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    songs = db.relationship('PlaylistSong', backref='playlist', lazy='dynamic', 
                           cascade='all, delete-orphan', order_by='PlaylistSong.position')
    
    def to_dict(self, include_songs=True):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'coverArt': self.cover_art,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'isLocal': False,
            'remoteId': self.id
        }
        
        if include_songs:
            data['songs'] = [ps.song_data for ps in self.songs.order_by(PlaylistSong.position)]
        
        return data


class PlaylistSong(db.Model):
    __tablename__ = 'playlist_songs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playlist_id = db.Column(db.String(36), db.ForeignKey('playlists.id'), nullable=False, index=True)
    song_id = db.Column(db.Integer, nullable=False)  # Local song ID from device
    song_data = db.Column(db.JSON, nullable=False)  # Full song metadata
    position = db.Column(db.Integer, nullable=False, default=0)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('playlist_id', 'song_id', name='unique_playlist_song'),
    )


class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    song_id = db.Column(db.Integer, nullable=False)  # Local song ID from device
    song_data = db.Column(db.JSON, nullable=False)  # Full song metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'song_id', name='unique_user_favorite'),
    )
    
    def to_dict(self):
        return self.song_data


class History(db.Model):
    __tablename__ = 'history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    song_id = db.Column(db.Integer, nullable=False)
    song_data = db.Column(db.JSON, nullable=False)
    played_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        data = dict(self.song_data)
        data['playedAt'] = self.played_at.isoformat()
        return data
