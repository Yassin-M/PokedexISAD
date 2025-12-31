from flask import Blueprint, render_template, request
from app.controller.model.eredu_kontroladorea import EreduKontroladorea


def taldeak_blueprint(db):
    taldeak_bp = Blueprint('taldeak', __name__, template_folder="../../templates")
    service = EreduKontroladorea(db)

    # Load taldeak names during initialization
    talde_zerrenda = service.taldeak_kargatu('juan')
    print("Loaded taldeak:", talde_zerrenda)  # Debugging output

    @taldeak_bp.route('/taldeak', methods=['GET', 'POST'])
    def taldeak_kargatu():
        talde_zerrenda = service.taldeak_kargatu('juan')
        return render_template('taldeak.html', taldeak=talde_zerrenda)

    return taldeak_bp
