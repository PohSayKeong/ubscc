import json
import logging

from flask import request

from routes import app

logger = logging.getLogger(__name__)


@app.route("/ub5-flags", methods=["POST"])
def decode():
    return json.dumps(
        {
            "sanityScroll": {"flag": "UB5{dzNsYzBtM183MF9jN2ZfTjB0dHlCMDE=}"},
            "openAiExploration": {"flag": "FLAG_CONTENT_HERE"},
            "dictionaryAttack": {
                "flag": "UB5{FLAG_CONTENT_HERE}",
                "password": "PASSWORD_HERE",
            },
            "pictureSteganography": {
                "flagOne": "UB5-1{1_am_d3f_n0t_old}}",
                "flagTwo": "UB5-2{1amlik3n3w}",
            },
            "reverseEngineeringTheDeal": {
                "flag": "FLAG_CONTENT_HERE",
                "key": "KEY_HERE",
            },
        }
    )
