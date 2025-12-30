from flask import Blueprint, render_template, request
from app.controller.model.eredu_kontroladorea import EreduKontroladorea

def itemdex_blueprint(db):

    bp = Blueprint("itemdex", __name__, template_folder="../../templates")
    service = EreduKontroladorea(db)

    @bp.route("/itemdex", methods=["GET", "POST"])
    def itemdex():
        iragazkiak = {
            "motak": [],
            "alfabetikokiAlderantziz": False
        }

        if request.method == "POST":
            iragazkiak["motak"] = request.form.getlist("motak")
            iragazkiak["alfabetikokiAlderantziz"] = (
                request.form.get("orden") == "desc"
            )

        items = service.itemdex_kargatu(iragazkiak)
        return render_template("itemdex.html", items=items)

    @bp.route("/itemdex/item/<int:id>")
    def item(id):
        item = service.bistaratu_item(id)
        return render_template("item.html", item=item)

    return bp
