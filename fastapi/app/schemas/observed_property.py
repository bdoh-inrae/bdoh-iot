from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


## OBSERVED PROPERTY ___________
class ObservedPropertyBase(BaseModel):
    name: str
    description: Optional[str] = None
    definition: str  # URI

class ObservedPropertyCreate(ObservedPropertyBase):
    """Schéma pour créer un ObservedProperty"""
    id: Optional[str] = None

class ObservedPropertyUpdate(BaseModel):
    """Mise à jour partielle"""
    name: Optional[str] = None
    description: Optional[str] = None
    definition: Optional[str] = None

class ObservedPropertyResponse(ObservedPropertyBase):
    """Schéma de réponse pour un ObservedProperty"""
    id: str
