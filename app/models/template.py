"""
Template Model - Marketplace Templates
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class TemplateCategory(Base):
    """Template category model"""
    __tablename__ = "template_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    sort_order = Column(Integer, default=0)
    
    # Relationships
    templates = relationship("Template", back_populates="category")
    
    def __repr__(self):
        return f"<TemplateCategory {self.name}>"


class Template(Base):
    """QR Code template model for marketplace"""
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("template_categories.id"), nullable=True)
    
    # Template Info
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=False)
    preview_image = Column(String, nullable=False)
    
    # Pricing
    price = Column(Float, nullable=False)  # In euros
    is_free = Column(Boolean, default=False)
    
    # Design Configuration (JSON with QR settings)
    design_config = Column(JSON, nullable=False)
    # Example: {
    #   "foreground_color": "#000000",
    #   "background_color": "#FFFFFF",
    #   "style": "rounded",
    #   "logo_path": "/templates/logos/restaurant.png"
    # }
    
    # Landing Page Template (if included)
    landing_page_template = Column(Text, nullable=True)  # HTML template
    
    # Files
    files = Column(JSON, nullable=True)  # List of included files
    
    # Stats
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    downloads = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    reviews_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="templates")
    category = relationship("TemplateCategory", back_populates="templates")
    purchases = relationship("TemplatePurchase", back_populates="template")
    
    def __repr__(self):
        return f"<Template {self.title} - €{self.price}>"


class TemplatePurchase(Base):
    """Template purchase tracking"""
    __tablename__ = "template_purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)
    
    # Payment
    amount = Column(Float, nullable=False)
    stripe_payment_intent_id = Column(String, nullable=True)
    
    # Timestamps
    purchased_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    template = relationship("Template", back_populates="purchases")
    
    def __repr__(self):
        return f"<TemplatePurchase {self.id}: Template {self.template_id} by User {self.user_id}>"
