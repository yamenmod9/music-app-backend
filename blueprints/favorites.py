from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import Favorite
from utils import error_response

favorites_bp = Blueprint('favorites', __name__, url_prefix='/api/favorites')


@favorites_bp.route('', methods=['GET'])
@jwt_required()
def get_favorites():
    current_user_id = get_jwt_identity()
    
    favorites = Favorite.query.filter_by(user_id=current_user_id)\
        .order_by(Favorite.created_at.desc()).all()
    
    return jsonify([f.to_dict() for f in favorites]), 200


@favorites_bp.route('', methods=['POST'])
@jwt_required()
def add_favorite():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'id' not in data:
        return error_response('Song data is required', 400)
    
    song_id = data['id']
    
    # Check if already favorited
    existing = Favorite.query.filter_by(
        user_id=current_user_id,
        song_id=song_id
    ).first()
    
    if existing:
        return jsonify({'message': 'Already in favorites'}), 200
    
    favorite = Favorite(
        user_id=current_user_id,
        song_id=song_id,
        song_data=data
    )
    
    db.session.add(favorite)
    db.session.commit()
    
    return jsonify({'message': 'Added to favorites'}), 200


@favorites_bp.route('/<int:song_id>', methods=['DELETE'])
@jwt_required()
def remove_favorite(song_id):
    current_user_id = get_jwt_identity()
    
    favorite = Favorite.query.filter_by(
        user_id=current_user_id,
        song_id=song_id
    ).first()
    
    if not favorite:
        return error_response('Favorite not found', 404)
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({'message': 'Removed from favorites'}), 200


@favorites_bp.route('/<int:song_id>/check', methods=['GET'])
@jwt_required()
def check_favorite(song_id):
    current_user_id = get_jwt_identity()
    
    favorite = Favorite.query.filter_by(
        user_id=current_user_id,
        song_id=song_id
    ).first()
    
    return jsonify({'is_favorite': favorite is not None}), 200
