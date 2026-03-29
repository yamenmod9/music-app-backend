from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import History
from utils import error_response

history_bp = Blueprint('history', __name__, url_prefix='/api/history')


@history_bp.route('', methods=['GET'])
@jwt_required()
def get_history():
    current_user_id = get_jwt_identity()
    limit = request.args.get('limit', 50, type=int)
    
    history = History.query.filter_by(user_id=current_user_id)\
        .order_by(History.played_at.desc())\
        .limit(min(limit, 100)).all()
    
    return jsonify([h.to_dict() for h in history]), 200


@history_bp.route('', methods=['POST'])
@jwt_required()
def add_to_history():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'id' not in data:
        return error_response('Song data is required', 400)
    
    song_id = data['id']
    
    # Remove old entry for same song if exists
    History.query.filter_by(
        user_id=current_user_id,
        song_id=song_id
    ).delete()
    
    history = History(
        user_id=current_user_id,
        song_id=song_id,
        song_data=data,
        played_at=datetime.utcnow()
    )
    
    db.session.add(history)
    
    # Keep only last 100 entries
    count = History.query.filter_by(user_id=current_user_id).count()
    if count > 100:
        oldest = History.query.filter_by(user_id=current_user_id)\
            .order_by(History.played_at.asc())\
            .limit(count - 100).all()
        for h in oldest:
            db.session.delete(h)
    
    db.session.commit()
    
    return jsonify({'message': 'Added to history'}), 200


@history_bp.route('', methods=['DELETE'])
@jwt_required()
def clear_history():
    current_user_id = get_jwt_identity()
    
    History.query.filter_by(user_id=current_user_id).delete()
    db.session.commit()
    
    return jsonify({'message': 'History cleared'}), 200
