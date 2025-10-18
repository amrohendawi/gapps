from flask import (
    jsonify
)
from . import api
from app.models import *
from app.utils.decorators import login_required
from app.utils.integrations import api_get


@api.route("/integrations", methods=["GET"])
@login_required
def list_integrations():
    """List all external integrations - get configured third-party service connections"""
    response = api_get("integrations")
    return jsonify(response)

@api.route("/deployments", methods=["GET"])
@login_required
def list_deployments():
    """List all deployments - get infrastructure deployments across integrated platforms"""
    response = api_get("deployments")
    return jsonify(response)

@api.route("/deployments/<string:id>", methods=["GET"])
@login_required
def get_deployment(id):
    """Get deployment details - retrieve information about a specific deployment"""
    response = api_get(f"deployments/{id}")
    return jsonify(response)

@api.route("/deployments/<string:id>/violations", methods=["GET"])
@login_required
def list_violations_for_deployment(id):
    """List violations for a deployment - get security or policy violations detected"""
    response = api_get(f"deployments/{id}/violations")
    return jsonify(response)

