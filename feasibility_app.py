import flet as ft
import json
import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Enums for better data management
class ProjectStatus(Enum):
    NEW = "Nuevo"
    UNDER_REVIEW = "En Revisión"
    FEASIBLE = "Factible"
    NOT_FEASIBLE = "No Factible"
    APPROVED = "Aprobado"
    REJECTED = "Rechazado"

class Priority(Enum):
    LOW = "Baja"
    MEDIUM = "Media"
    HIGH = "Alta"
    CRITICAL = "Crítica"

class Department(Enum):
    SALES = "Ventas"
    PROJECTS = "Proyectos"
    ENGINEERING = "Ingeniería"
    PRODUCTION = "Producción"
    QUALITY = "Calidad"
    FINANCE = "Finanzas"
    PROCUREMENT = "Compras"
    LOGISTICS = "Logística"


# Data models
@dataclass
class ProjectInfo:
    id: int
    project_name: str
    customer_name: str
    customer_contact: str
    customer_email: str
    customer_phone: str
    project_description: str
    expected_volume: str
    target_price: float
    target_margin: float
    delivery_date: str
    technical_requirements: str
    quality_requirements: str
    regulatory_requirements: str
    priority: str
    status: str
    created_by: str
    created_date: str
    last_updated: str
    assigned_departments: List[str]
    feasibility_score: int
    risk_factors: List[str]
    opportunities: List[str]
    comments: List[Dict]
    technical_drawings_pdf: List[str]
    technical_drawings_step: List[str]

# State management class
class FeasibilityState:
    def __init__(self):
        self.projects = [
            ProjectInfo(
                id=1,
                project_name="LUCID ATLAS IM",
                customer_name="LUCID",
                customer_contact="Nidhishri Tapadia",
                customer_email="NidhishriTapadia@lucidmotors.com",
                customer_phone="+1 608 692 6323",
                project_description="Estampado de rotor y estator para motor IM + Die casting RT + Torneado RT + Lavado RT",
                expected_volume="25,000 sets/año",
                target_price=150,
                target_margin=8.0,
                delivery_date="2026-03-17",
                technical_requirements="ISO 9001, IATF 16949, Especificados en dibujos",
                quality_requirements="Especificados en dibujos",
                regulatory_requirements="Normas automotrices mexicanas y estadounidenses, Especificados en dibujos",
                priority=Priority.HIGH.value,
                status=ProjectStatus.UNDER_REVIEW.value,
                created_by="Jorge Valdés",
                created_date="2025-10-16",
                last_updated="2025-10-16",
                assigned_departments=[Department.ENGINEERING.value, Department.QUALITY.value, Department.SALES.value, Department.PROJECTS.value],
                feasibility_score=75,
                risk_factors=["Alta competencia", "Requisitos técnicos complejos", "Nuevos procesos", "Mucha inversión", "Bajo volumen", "Dibujos no congelados"],
                opportunities=["Mercado en crecimiento", "Cliente nuevo", "Nuevos procesos"],
                comments=[

                ],
                technical_drawings_pdf=[],
                technical_drawings_step=[]
            ),
            
        ]
        self.next_id = 3
        self.filter_status = "Todos"
        self.filter_priority = "Todas"
        self.search_term = ""

    def add_project(self, project: ProjectInfo):
        project.id = self.next_id
        self.next_id += 1
        self.projects.append(project)

    def update_project(self, project_id: int, updates: Dict):
        for project in self.projects:
            if project.id == project_id:
                for key, value in updates.items():
                    setattr(project, key, value)
                project.last_updated = datetime.datetime.now().strftime("%Y-%m-%d")
                break

    def get_projects(self) -> List[ProjectInfo]:
        filtered = self.projects
        
        if self.filter_status != "Todos":
            filtered = [p for p in filtered if p.status == self.filter_status]
        
        if self.filter_priority != "Todas":
            filtered = [p for p in filtered if p.priority == self.filter_priority]
        
        if self.search_term:
            filtered = [p for p in filtered 
                       if self.search_term.lower() in p.project_name.lower() 
                       or self.search_term.lower() in p.customer_name.lower()]
        
        return filtered

    def add_comment(self, project_id: int, comment: str):
        for project in self.projects:
            if project.id == project_id:
                new_comment = {
                    "comment": comment,
                    "date": datetime.datetime.now().strftime("%Y-%m-%d")
                }
                project.comments.append(new_comment)
                project.last_updated = datetime.datetime.now().strftime("%Y-%m-%d")
                break

# Global state instance
state = FeasibilityState()

# Global modal reference for better management
current_modal = None

# Global project list reference for updates
project_list_ref = None

# Global statistics reference for updates
stats_row_ref = None

def force_close_all_modals(page: ft.Page):
    """Emergency function to close all modals and clear overlays"""
    global current_modal
    try:
        # Clear all overlays
        page.overlay.clear()
        current_modal = None
        page.update()
        print("All modals force closed")
    except Exception as e:
        print(f"Error force closing modals: {e}")

# UI Components
def create_project_card(project: ProjectInfo, page: ft.Page):
    def get_status_color(status: str):
        colors = {
            ProjectStatus.NEW.value: "#4A90E2",  # Modern blue
            ProjectStatus.UNDER_REVIEW.value: "#F5A623",  # Warm orange
            ProjectStatus.FEASIBLE.value: "#00BFA5",  # Teal/cyan
            ProjectStatus.NOT_FEASIBLE.value: "#E53E3E",  # Modern red
            ProjectStatus.APPROVED.value: "#00BFA5",  # Teal/cyan
            ProjectStatus.REJECTED.value: "#E53E3E"  # Modern red
        }
        return colors.get(status, "#9B9B9B")  # Light grey

    def get_priority_color(priority: str):
        colors = {
            Priority.LOW.value: "#00BFA5",  # Teal/cyan
            Priority.MEDIUM.value: "#4A90E2",  # Modern blue
            Priority.HIGH.value: "#F5A623",  # Warm orange
            Priority.CRITICAL.value: "#E53E3E"  # Modern red
        }
        return colors.get(priority, "#9B9B9B")  # Light grey

    def open_project_details(e):
        show_project_details_modal(page, project)

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.BUSINESS, color="#4A90E2", size=20),
                ft.Text(project.project_name, weight="bold", size=16, expand=True),
                ft.Container(
                    content=ft.Text(project.priority, size=10, color=ft.Colors.WHITE),
                    bgcolor=get_priority_color(project.priority),
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=8, vertical=2)
                )
            ]),
            ft.Text(f"Cliente: {project.customer_name}", size=12, color="#6B7280"),
            ft.Text(f"Contacto: {project.customer_contact}", size=11, color="#6B7280"),
            ft.Row([
                ft.Container(
                    content=ft.Text(project.status, size=11, color=ft.Colors.WHITE),
                    bgcolor=get_status_color(project.status),
                    border_radius=12,
                    padding=ft.padding.symmetric(horizontal=10, vertical=2)
                ),
                ft.Text(f"Score: {project.feasibility_score}%", size=11, weight="bold", color="#4A90E2")
            ]),
            ft.Row([
                ft.Icon(ft.Icons.ATTACH_MONEY, size=14, color="#00BFA5"),
                ft.Text(f"${project.target_price:.2f}", size=11, color="#00BFA5"),
                ft.Icon(ft.Icons.TRENDING_UP, size=14, color="#4A90E2"),
                ft.Text(f"{project.target_margin}% margen", size=11, color="#4A90E2")
            ]),
            ft.Text(f"Volumen: {project.expected_volume}", size=11, color="#6B7280"),
            ft.Text(f"Entrega: {project.delivery_date}", size=11, color="#6B7280"),
            ft.Row([
                ft.Icon(ft.Icons.PERSON, size=12, color="#6B7280"),
                ft.Text(f"Por: {project.created_by}", size=10, color="#6B7280"),
                ft.Text(f"• {project.last_updated}", size=10, color="#6B7280")
            ])
        ]),
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
        padding=15,
        margin=5,
        shadow=ft.BoxShadow(blur_radius=5, spread_radius=1, color=ft.Colors.GREY_300),
        width=350,
        on_click=open_project_details
    )

def show_project_details_modal(page: ft.Page, project: ProjectInfo):
    def get_status_color(status: str):
        colors = {
            ProjectStatus.NEW.value: "#4A90E2",  # Modern blue
            ProjectStatus.UNDER_REVIEW.value: "#F5A623",  # Warm orange
            ProjectStatus.FEASIBLE.value: "#00BFA5",  # Teal/cyan
            ProjectStatus.NOT_FEASIBLE.value: "#E53E3E",  # Modern red
            ProjectStatus.APPROVED.value: "#00BFA5",  # Teal/cyan
            ProjectStatus.REJECTED.value: "#E53E3E"  # Modern red
        }
        return colors.get(status, "#9B9B9B")  # Light grey

    # Comments section
    comments_list = ft.Column([])

    # Add comment section
    new_comment_field = ft.TextField(
        label="Agregar comentario",
        multiline=True,
        max_lines=3
    )
    
    def add_comment(e):
        if new_comment_field.value.strip():
            state.add_comment(project.id, new_comment_field.value)
            new_comment_field.value = ""
            # Update the comments section without recreating the entire modal
            update_comments_section()
            page.update()
    
    def update_comments_section():
        # Clear existing comments and rebuild
        comments_list.controls.clear()
        comments_list.controls.append(ft.Text("Comentarios del Equipo", size=16, weight="bold"))
        comments_list.controls.append(ft.Divider())
        
        # Add existing comments
        for comment in project.comments:
            comments_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(comment["date"], size=10, color=ft.Colors.GREY)
                        ]),
                        ft.Text(comment["comment"], size=12)
                    ]),
                    bgcolor=ft.Colors.GREY_100,
                    padding=10,
                    margin=5,
                    border_radius=8
                )
            )
        
        # Add the comment input section
        comments_list.controls.extend([
            new_comment_field,
            ft.ElevatedButton(
                "Agregar Comentario",
                on_click=add_comment,
                bgcolor="#4A90E2",
                color=ft.Colors.WHITE
            )
        ])
    
    # Initialize the comments section
    update_comments_section()

    modal_content = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Detalles del Proyecto", size=20, weight="bold", expand=True),
                ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: setattr(modal, "open", False) or page.update())
            ]),
            ft.Divider(),
            
            # Project header
            ft.Row([
                ft.Column([
                    ft.Text(project.project_name, size=18, weight="bold"),
                    ft.Text(f"Cliente: {project.customer_name}", size=14),
                    ft.Text(f"Contacto: {project.customer_contact}", size=12, color=ft.Colors.GREY)
                ], expand=True),
                ft.Column([
                    ft.Container(
                        content=ft.Text(project.status, color=ft.Colors.WHITE),
                        bgcolor=get_status_color(project.status),
                        border_radius=12,
                        padding=ft.padding.symmetric(horizontal=12, vertical=4)
                    ),
                    ft.Text(f"Score: {project.feasibility_score}%", size=14, weight="bold", color="#4A90E2")
                ])
            ]),
            
            ft.Divider(),
            
            # Project details
            ft.Row([
                ft.Column([
                    ft.Text("Información del Proyecto", size=16, weight="bold"),
                    ft.Text(f"Descripción: {project.project_description}", size=12),
                    ft.Text(f"Volumen Esperado en Sets: {project.expected_volume}", size=12),
                    ft.Text(f"Fecha de Entrega primeras piezas: {project.delivery_date}", size=12),
                    ft.Text(f"Precio Set: ${project.target_price:.2f}", size=12),
                    ft.Text(f"Margen Objetivo Set USD: {project.target_margin}%", size=12)
                ], expand=True),
                ft.Column([
                    ft.Text("Requisitos", size=16, weight="bold"),
                    ft.Text(f"Técnicos: {project.technical_requirements}", size=12),
                    ft.Text(f"Calidad: {project.quality_requirements}", size=12),
                    ft.Text(f"Regulatorios: {project.regulatory_requirements}", size=12)
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            # Risk and opportunities
            ft.Row([
                ft.Column([
                    ft.Text("Factores de Riesgo", size=14, weight="bold", color="#E53E3E"),
                    ft.Column([ft.Text(f"• {risk}", size=11) for risk in project.risk_factors])
                ], expand=True),
                ft.Column([
                    ft.Text("Oportunidades", size=14, weight="bold", color="#00BFA5"),
                    ft.Column([ft.Text(f"• {opp}", size=11) for opp in project.opportunities])
                ], expand=True)
            ]),
            
            ft.Divider(),
            
            # Comments section
            comments_list
        ], scroll=ft.ScrollMode.AUTO),
        width=800,
        height=600,
        padding=20
    )

    # Create a custom modal using Container for better control
    modal = ft.Container(
        content=ft.Column([
            # Modal header
            ft.Row([
                ft.Text("Detalles del Proyecto", size=18, weight="bold", expand=True),
                ft.IconButton(
                    ft.Icons.EDIT,
                    on_click=lambda e: edit_project_modal(page, project),
                    tooltip="Editar Proyecto",
                    icon_color="#4A90E2"
                ),
                ft.IconButton(
                    ft.Icons.CLOSE,
                    on_click=lambda e: close_modal(modal, page),
                    tooltip="Cerrar"
                )
            ]),
            ft.Divider(),
            # Modal content
            modal_content
        ]),
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
        padding=20,
        width=900,
        height=700,
        shadow=ft.BoxShadow(blur_radius=20, spread_radius=5, color=ft.Colors.BLACK26),
        visible=True
    )
    
    # Create overlay background
    overlay = ft.Container(
        content=modal,
        bgcolor=ft.Colors.BLACK26,
        alignment=ft.alignment.center,
        expand=True,
        visible=True,
        on_click=lambda e: close_modal(modal, page) if e.target == overlay else None
    )
    
    # Clear any existing modals and add this one
    page.overlay.clear()
    page.overlay.append(overlay)
    page.update()

def close_modal(modal, page: ft.Page):
    """Properly close the modal and clean up"""
    global current_modal
    
    try:
        # Hide the modal by setting visibility to False
        if hasattr(modal, 'visible'):
            modal.visible = False
        
        # Remove from overlay if it exists
        if modal in page.overlay:
            page.overlay.remove(modal)
        
        # Clear global reference
        if current_modal == modal:
            current_modal = None
        
        # Force a complete page refresh
        page.update()
        
        # Additional cleanup - ensure overlay is completely clear
        page.overlay.clear()
        page.update()
        
        print("Modal closed successfully")
        
    except Exception as e:
        print(f"Error closing modal: {e}")
        # Emergency cleanup
        try:
            page.overlay.clear()
            current_modal = None
            page.update()
            print("Emergency modal cleanup completed")
        except:
            pass

def edit_project_modal(page: ft.Page, project: ProjectInfo):
    """Create edit project modal with pre-filled form"""
    global current_modal
    
    # Force close any existing modals first
    force_close_all_modals(page)
    
    # Form fields with pre-filled values
    project_name_field = ft.TextField(
        label="Nombre del Proyecto *", 
        hint_text="Ej: Tesla Everest",
        value=project.project_name,
        width=300,
        autofocus=True
    )
    customer_name_field = ft.TextField(
        label="Nombre del Cliente *", 
        hint_text="Ej: Tesla Inc.",
        value=project.customer_name,
        width=300
    )
    customer_contact_field = ft.TextField(
        label="Contacto del Cliente *", 
        hint_text="Ej: Juan Pérez",
        value=project.customer_contact,
        width=300
    )
    customer_email_field = ft.TextField(
        label="Email del Cliente *", 
        hint_text="juan.perez@tesla.com",
        value=project.customer_email,
        width=300
    )
    customer_phone_field = ft.TextField(
        label="Teléfono del Cliente", 
        hint_text="+52 55 1234 5678",
        value=project.customer_phone,
        width=300
    )
    
    description_field = ft.TextField(
        label="Descripción del Proyecto *", 
        hint_text="Descripción detallada del proyecto y sus objetivos",
        value=project.project_description,
        multiline=True, 
        max_lines=3,
        width=300
    )
    
    # Commercial information
    volume_field = ft.TextField(
        label="Volumen Esperado en Sets *", 
        hint_text="Ej: 50,000 pcs/año",
        value=project.expected_volume,
        width=300
    )
    price_field = ft.TextField(
        label="Precio Objetivo (USD) en Sets *", 
        hint_text="25.50",
        value=str(project.target_price),
        width=300
    )
    margin_field = ft.TextField(
        label="Margen Objetivo (%)", 
        hint_text="15.0",
        value=str(project.target_margin),
        width=300
    )
    delivery_field = ft.TextField(
        label="Fecha de Entrega *", 
        hint_text="Año-Mes-Día",
        value=project.delivery_date,
        width=300
    )
    
    # Technical requirements
    tech_requirements_field = ft.TextField(
        label="Requisitos Técnicos", 
        hint_text="Especificaciones técnicas, materiales, tolerancias",
        value=project.technical_requirements,
        multiline=True, 
        max_lines=3,
        width=300
    )
    quality_requirements_field = ft.TextField(
        label="Requisitos de Calidad", 
        hint_text="Estándares de calidad, certificaciones requeridas",
        value=project.quality_requirements,
        multiline=True, 
        max_lines=3,
        width=300
    )
    regulatory_requirements_field = ft.TextField(
        label="Requisitos Regulatorios", 
        hint_text="Normas, regulaciones, certificaciones",
        value=project.regulatory_requirements,
        multiline=True, 
        max_lines=3,
        width=300
    )
    
    # Project management
    priority_dropdown = ft.Dropdown(
        label="Prioridad *",
        options=[ft.dropdown.Option(p.value) for p in Priority],
        value=project.priority,
        width=300
    )
    
    status_dropdown = ft.Dropdown(
        label="Estado *",
        options=[ft.dropdown.Option(s.value) for s in ProjectStatus],
        value=project.status,
        width=300
    )
    
    # Department assignments
    dept1_dropdown = ft.Dropdown(
        label="Departamento Principal *",
        options=[ft.dropdown.Option(d.value) for d in Department],
        value=project.assigned_departments[0] if project.assigned_departments else None,
        width=200
    )
    dept2_dropdown = ft.Dropdown(
        label="Departamento Secundario",
        options=[ft.dropdown.Option(d.value) for d in Department],
        value=project.assigned_departments[1] if len(project.assigned_departments) > 1 else None,
        width=200
    )
    dept3_dropdown = ft.Dropdown(
        label="Departamento Adicional",
        options=[ft.dropdown.Option(d.value) for d in Department],
        value=project.assigned_departments[2] if len(project.assigned_departments) > 2 else None,
        width=200
    )
    
    # Dynamic Risk and opportunities containers
    risk_factors_container = ft.Column([])
    opportunities_container = ft.Column([])
    
    # Lists to store dynamic fields
    risk_fields = []
    opp_fields = []
    
    def create_risk_field(index, value=""):
        field = ft.TextField(
            label=f"Factor de Riesgo {index + 1}",
            hint_text="Ej: Alta competencia en el mercado",
            value=value,
            width=200
        )
        return field
    
    def create_opp_field(index, value=""):
        field = ft.TextField(
            label=f"Oportunidad {index + 1}",
            hint_text="Ej: Nuevo cliente",
            value=value,
            width=200
        )
        return field
    
    def add_risk_field(e):
        new_field = create_risk_field(len(risk_fields))
        risk_fields.append(new_field)
        risk_factors_container.controls.append(new_field)
        page.update()
    
    def add_opp_field(e):
        new_field = create_opp_field(len(opp_fields))
        opp_fields.append(new_field)
        opportunities_container.controls.append(new_field)
        page.update()
    
    def remove_risk_field(field_to_remove):
        if field_to_remove in risk_fields:
            risk_fields.remove(field_to_remove)
            risk_factors_container.controls.remove(field_to_remove)
            # Update labels
            for i, field in enumerate(risk_fields):
                field.label = f"Factor de Riesgo {i + 1}"
            page.update()
    
    def remove_opp_field(field_to_remove):
        if field_to_remove in opp_fields:
            opp_fields.remove(field_to_remove)
            opportunities_container.controls.remove(field_to_remove)
            # Update labels
            for i, field in enumerate(opp_fields):
                field.label = f"Oportunidad {i + 1}"
            page.update()
    
    # Initialize with existing data
    for i, risk in enumerate(project.risk_factors):
        field = create_risk_field(i, risk)
        risk_fields.append(field)
        risk_factors_container.controls.append(field)
    
    for i, opp in enumerate(project.opportunities):
        field = create_opp_field(i, opp)
        opp_fields.append(field)
        opportunities_container.controls.append(field)
    
    # Add buttons to add more fields
    add_risk_button = ft.ElevatedButton(
        "+ Agregar Factor de Riesgo",
        on_click=add_risk_field,
        bgcolor="#E53E3E",
        color=ft.Colors.WHITE,
        height=35,
        width=200
    )
    
    add_opp_button = ft.ElevatedButton(
        "+ Agregar Oportunidad",
        on_click=add_opp_field,
        bgcolor="#00BFA5",
        color=ft.Colors.WHITE,
        height=35,
        width=200
    )
    
    risk_factors_container.controls.append(add_risk_button)
    opportunities_container.controls.append(add_opp_button)
    
    # Error message
    error_text = ft.Text(
        "",
        color="#E53E3E",
        visible=False,
        size=12
    )

    # Validation function
    def validate_form():
        required_fields = [
            (project_name_field, "Nombre del Proyecto"),
            (customer_name_field, "Nombre del Cliente"),
            (customer_contact_field, "Contacto del Cliente"),
            (customer_email_field, "Email del Cliente"),
            (description_field, "Descripción del Proyecto"),
            (volume_field, "Volumen Esperado"),
            (price_field, "Precio Objetivo"),
            (delivery_field, "Fecha de Entrega"),
            (priority_dropdown, "Prioridad"),
            (status_dropdown, "Estado")
        ]
        
        missing_fields = []
        for field, label in required_fields:
            if not field.value or field.value.strip() == "":
                missing_fields.append(label)
        
        if missing_fields:
            error_text.value = f"Campos requeridos faltantes: {', '.join(missing_fields)}"
            error_text.visible = True
            page.update()
            return False
        
        # Validate email format
        if customer_email_field.value and "@" not in customer_email_field.value:
            error_text.value = "Formato de email inválido"
            error_text.visible = True
            page.update()
            return False
        
        # Validate numeric fields
        try:
            if price_field.value:
                float(price_field.value)
            if margin_field.value:
                float(margin_field.value)
        except ValueError:
            error_text.value = "Los campos de precio y margen deben ser números válidos"
            error_text.visible = True
            page.update()
            return False
        
        error_text.visible = False
        page.update()
        return True

    def save_changes(e):
        if not validate_form():
            return
            
        try:
            # Update project with new values
            updates = {
                'project_name': project_name_field.value.strip(),
                'customer_name': customer_name_field.value.strip(),
                'customer_contact': customer_contact_field.value.strip(),
                'customer_email': customer_email_field.value.strip(),
                'customer_phone': customer_phone_field.value.strip() if customer_phone_field.value else "",
                'project_description': description_field.value.strip(),
                'expected_volume': volume_field.value.strip(),
                'target_price': float(price_field.value) if price_field.value else 0.0,
                'target_margin': float(margin_field.value) if margin_field.value else 0.0,
                'delivery_date': delivery_field.value.strip(),
                'technical_requirements': tech_requirements_field.value.strip() if tech_requirements_field.value else "",
                'quality_requirements': quality_requirements_field.value.strip() if quality_requirements_field.value else "",
                'regulatory_requirements': regulatory_requirements_field.value.strip() if regulatory_requirements_field.value else "",
                'priority': priority_dropdown.value,
                'status': status_dropdown.value,
                'assigned_departments': [dept for dept in [dept1_dropdown.value, dept2_dropdown.value, dept3_dropdown.value] if dept],
                'risk_factors': [risk.strip() for risk in [field.value for field in risk_fields] if risk and risk.strip()],
                'opportunities': [opp.strip() for opp in [field.value for field in opp_fields] if opp and opp.strip()]
            }
            
            state.update_project(project.id, updates)
            close_modal(modal, page)
            # Small delay to ensure modal is fully closed before refreshing
            import time
            time.sleep(0.1)
            update_dashboard(page)  # Refresh the dashboard after updating project
            
        except Exception as ex:
            error_text.value = f"Error al actualizar el proyecto: {str(ex)}"
            error_text.visible = True
            page.update()

    def clear_form(e):
        # Clear all fields
        for field in [project_name_field, customer_name_field, customer_contact_field, 
                     customer_email_field, customer_phone_field, description_field,
                     volume_field, price_field, margin_field, delivery_field,
                     tech_requirements_field, quality_requirements_field, 
                     regulatory_requirements_field]:
            field.value = ""
        
        # Clear dynamic fields
        for field in risk_fields:
            field.value = ""
        for field in opp_fields:
            field.value = ""
        
        for dropdown in [priority_dropdown, status_dropdown, dept1_dropdown, dept2_dropdown, dept3_dropdown]:
            dropdown.value = None
        
        error_text.visible = False
        page.update()

    # Create tabbed interface for better organization
    basic_info_tab = ft.Column([
        ft.Text("Información Básica del Proyecto", size=16, weight="bold", color="#4A90E2"),
        ft.Row([
            ft.Column([
                project_name_field,
                customer_name_field,
                customer_contact_field,
                customer_email_field,
                customer_phone_field
            ], expand=True),
            ft.Column([
                description_field,
                priority_dropdown,
                status_dropdown
            ], expand=True)
        ])
    ], scroll=ft.ScrollMode.AUTO)
    
    commercial_tab = ft.Column([
        ft.Text("Información Comercial", size=16, weight="bold", color="#00BFA5"),
        ft.Row([
            ft.Column([
                volume_field,
                price_field,
                margin_field,
                delivery_field
            ], expand=True)
        ])
    ], scroll=ft.ScrollMode.AUTO)
    
    technical_tab = ft.Column([
        ft.Text("Requisitos Técnicos y de Calidad", size=16, weight="bold", color="#F5A623"),
        ft.Row([
            ft.Column([
                tech_requirements_field,
                quality_requirements_field
            ], expand=True),
            ft.Column([
                regulatory_requirements_field
            ], expand=True)
        ])
    ], scroll=ft.ScrollMode.AUTO)
    
    team_tab = ft.Column([
        ft.Text("Asignación de Equipos y Evaluación", size=16, weight="bold", color=ft.Colors.PURPLE),
        ft.Row([
            ft.Column([
                ft.Text("Departamentos Asignados", size=14, weight="bold"),
                dept1_dropdown,
                dept2_dropdown,
                dept3_dropdown
            ], expand=True),
            ft.Column([
                ft.Text("Factores de Riesgo", size=14, weight="bold"),
                risk_factors_container
            ], expand=True),
            ft.Column([
                ft.Text("Oportunidades", size=14, weight="bold"),
                opportunities_container
            ], expand=True)
        ])
    ], scroll=ft.ScrollMode.AUTO)

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Información Básica",
                icon=ft.Icons.INFO,
                content=basic_info_tab
            ),
            ft.Tab(
                text="Información Comercial",
                icon=ft.Icons.ATTACH_MONEY,
                content=commercial_tab
            ),
            ft.Tab(
                text="Requisitos Técnicos",
                icon=ft.Icons.ENGINEERING,
                content=technical_tab
            ),
            ft.Tab(
                text="Equipos y Evaluación",
                icon=ft.Icons.GROUP,
                content=team_tab
            )
        ],
        expand=True
    )

    # Create a custom modal using Container for better control
    modal = ft.Container(
        content=None,  # Will be set below
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
        padding=20,
        width=900,
        height=800,
        shadow=ft.BoxShadow(blur_radius=20, spread_radius=5, color=ft.Colors.BLACK26),
        visible=True
    )

    # Create buttons first for testing
    cancel_button = ft.ElevatedButton(
        "Cancelar",
        icon=ft.Icons.CANCEL,
        on_click=lambda e: close_modal(modal, page),
        bgcolor=ft.Colors.GREY_400,
        color=ft.Colors.WHITE,
        height=50,
        width=150
    )
    
    save_button = ft.ElevatedButton(
        "Guardar Cambios",
        icon=ft.Icons.SAVE,
        bgcolor="#00BFA5",
        color=ft.Colors.WHITE,
        on_click=save_changes,
        height=50,
        width=200
    )
    
    # Create scrollable content (without buttons)
    scrollable_content = ft.Column([
        error_text,
        tabs
    ], scroll=ft.ScrollMode.AUTO, expand=True)
    
    # Create modal content with fixed buttons at bottom
    modal_content = ft.Column([
        scrollable_content,
        ft.Divider(),
        ft.Container(
            content=ft.Row([
                cancel_button,
                save_button
            ], alignment=ft.MainAxisAlignment.END, spacing=10),
            bgcolor=ft.Colors.GREY_100,
            padding=10,
            border_radius=5
        )
    ], expand=True)

    # Update modal content
    modal.content = ft.Column([
        # Modal header
        ft.Row([
            ft.Text("Editar Proyecto", size=18, weight="bold", expand=True),
            ft.IconButton(
                ft.Icons.CLOSE,
                on_click=lambda e: close_modal(modal, page),
                tooltip="Cerrar"
            )
        ]),
        ft.Divider(),
        # Modal content
        modal_content
    ], expand=True)
    
    # Create overlay background
    overlay = ft.Container(
        content=modal,
        bgcolor=ft.Colors.BLACK26,
        alignment=ft.alignment.center,
        expand=True,
        visible=True,
        on_click=lambda e: close_modal(modal, page) if e.target == overlay else None
    )
    
    # Set global reference and add to overlay
    current_modal = overlay
    page.overlay.append(overlay)
    
    page.update()

def create_new_project_form(page: ft.Page):
    global current_modal
    
    # Force close any existing modals first
    force_close_all_modals(page)
    
    # Form fields with better organization
    project_name_field = ft.TextField(
        label="Nombre del Proyecto *", 
        hint_text="Ej: Tesla Everest",
        width=300,
        autofocus=True
    )
    customer_name_field = ft.TextField(
        label="Nombre del Cliente *", 
        hint_text="Ej: Tesla Inc.",
        width=300
    )
    customer_contact_field = ft.TextField(
        label="Contacto del Cliente *", 
        hint_text="Ej: Juan Pérez",
        width=300
    )
    customer_email_field = ft.TextField(
        label="Email del Cliente *", 
        hint_text="juan.perez@tesla.com",
        width=300
    )
    customer_phone_field = ft.TextField(
        label="Teléfono del Cliente", 
        hint_text="+52 55 1234 5678",
        width=300
    )
    customer_address_field = ft.TextField(
        label="Dirección del Cliente",
        hint_text="Dirección completa del cliente",
        width=300
    )
    customer_website_field = ft.TextField(
        label="Sitio Web del Cliente",
        hint_text="https://www.tesla.com",
        width=300
    )
    
    description_field = ft.TextField(
        label="Descripción del Proyecto *", 
        hint_text="Descripción detallada del proyecto y sus objetivos",
        multiline=True, 
        max_lines=3,
        width=300
    )
    
    # Commercial information
    volume_field = ft.TextField(
        label="Volumen Esperado *", 
        hint_text="Ej: 50,000 pcs/año",
        width=300
    )
    price_field = ft.TextField(
        label="Precio Objetivo (USD) *", 
        hint_text="25.50",
        width=300
    )
    margin_field = ft.TextField(
        label="Margen Objetivo (%)", 
        hint_text="15.0",
        width=300
    )
    delivery_field = ft.TextField(
        label="Fecha de Entrega *", 
        hint_text="2024-06-30",
        width=300
    )
    contract_duration_field = ft.TextField(
        label="Duración del Contrato",
        hint_text="Ej: 3 años",
        width=300
    )
    payment_terms_field = ft.TextField(
        label="Términos de Pago",
        hint_text="Ej: 30 días neto",
        width=300
    )
    
    # Technical requirements
    tech_requirements_field = ft.TextField(
        label="Requisitos Técnicos", 
        hint_text="Especificaciones técnicas, materiales, tolerancias",
        multiline=True, 
        max_lines=3,
        width=300
    )
    quality_requirements_field = ft.TextField(
        label="Requisitos de Calidad", 
        hint_text="Estándares de calidad, certificaciones requeridas",
        multiline=True, 
        max_lines=3,
        width=300
    )
    regulatory_requirements_field = ft.TextField(
        label="Requisitos Regulatorios", 
        hint_text="Normas, regulaciones, certificaciones",
        multiline=True, 
        max_lines=3,
        width=300
    )
    
    # Document selectors for technical drawings
    pdf_files = []
    step_files = []
    
    def on_pdf_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            for file in e.files:
                # Validate file extension
                if file.path.lower().endswith('.pdf'):
                    pdf_files.append(file.path)
                else:
                    # Show error message for invalid file type
                    error_text.value = f"Archivo inválido: {file.path.split('/')[-1]}. Solo se permiten archivos PDF."
                    error_text.visible = True
                    page.update()
            update_document_display()
    
    def on_step_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            for file in e.files:
                # Validate file extension
                if file.path.lower().endswith(('.stp', '.step')):
                    step_files.append(file.path)
                else:
                    # Show error message for invalid file type
                    error_text.value = f"Archivo inválido: {file.path.split('/')[-1]}. Solo se permiten archivos STEP (.stp, .step)."
                    error_text.visible = True
                    page.update()
            update_document_display()
    
    def update_document_display():
        # Clear existing display
        pdf_display.controls.clear()
        step_display.controls.clear()
        
        # Add PDF files
        for i, file_path in enumerate(pdf_files):
            pdf_display.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PICTURE_AS_PDF, color="#E53E3E", size=16),
                        ft.Text(f"PDF {i+1}: {file_path.split('/')[-1]}", size=12),
                        ft.IconButton(
                            ft.Icons.DELETE,
                            on_click=lambda e, idx=i: remove_pdf_file(idx),
                            icon_color="#E53E3E",
                            icon_size=16
                        )
                    ]),
                    bgcolor=ft.Colors.RED_50,
                    padding=5,
                    margin=2,
                    border_radius=5
                )
            )
        
        # Add STEP files
        for i, file_path in enumerate(step_files):
            step_display.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ENGINEERING, color="#4A90E2", size=16),
                        ft.Text(f"STEP {i+1}: {file_path.split('/')[-1]}", size=12),
                        ft.IconButton(
                            ft.Icons.DELETE,
                            on_click=lambda e, idx=i: remove_step_file(idx),
                            icon_color="#E53E3E",
                            icon_size=16
                        )
                    ]),
                    bgcolor=ft.Colors.BLUE_50,
                    padding=5,
                    margin=2,
                    border_radius=5
                )
            )
        
        page.update()
    
    def remove_pdf_file(index):
        if 0 <= index < len(pdf_files):
            pdf_files.pop(index)
            update_document_display()
    
    def remove_step_file(index):
        if 0 <= index < len(step_files):
            step_files.pop(index)
            update_document_display()
    
    # File pickers
    pdf_picker = ft.FilePicker(
        on_result=on_pdf_file_picked
    )
    step_picker = ft.FilePicker(
        on_result=on_step_file_picked
    )
    
    # Document display containers
    pdf_display = ft.Column([])
    step_display = ft.Column([])
    
    # Add file pickers to page
    page.overlay.append(pdf_picker)
    page.overlay.append(step_picker)
    
    # Project management
    priority_dropdown = ft.Dropdown(
        label="Prioridad *",
        options=[ft.dropdown.Option(p.value) for p in Priority],
        width=300
    )
    
    project_type_dropdown = ft.Dropdown(
        label="Tipo de Proyecto",
        options=[
            ft.dropdown.Option("Nuevo Proyecto"),
            ft.dropdown.Option("Cambio de ingeniería"),
            ft.dropdown.Option("Incremento de Capacidad"),
        ],
        width=300
    )
    
    # Department assignments
    dept1_dropdown = ft.Dropdown(
        label="Departamento Principal *",
        options=[ft.dropdown.Option(d.value) for d in Department],
        width=200
    )
    dept2_dropdown = ft.Dropdown(
        label="Departamento Secundario",
        options=[ft.dropdown.Option(d.value) for d in Department],
        width=200
    )
    dept3_dropdown = ft.Dropdown(
        label="Departamento Adicional",
        options=[ft.dropdown.Option(d.value) for d in Department],
        width=200
    )
    
    # Dynamic Risk and opportunities containers for new project
    new_risk_factors_container = ft.Column([])
    new_opportunities_container = ft.Column([])
    
    # Lists to store dynamic fields for new project
    new_risk_fields = []
    new_opp_fields = []
    
    def create_new_risk_field(index, value=""):
        field = ft.TextField(
            label=f"Factor de Riesgo {index + 1}",
            hint_text="Ej: Alta competencia en el mercado",
            value=value,
            width=200
        )
        return field
    
    def create_new_opp_field(index, value=""):
        field = ft.TextField(
            label=f"Oportunidad {index + 1}",
            hint_text="Ej: Mercado en crecimiento",
            value=value,
            width=200
        )
        return field
    
    def add_new_risk_field(e):
        new_field = create_new_risk_field(len(new_risk_fields))
        new_risk_fields.append(new_field)
        new_risk_factors_container.controls.append(new_field)
        page.update()
    
    def add_new_opp_field(e):
        new_field = create_new_opp_field(len(new_opp_fields))
        new_opp_fields.append(new_field)
        new_opportunities_container.controls.append(new_field)
        page.update()
    
    # Add initial fields
    initial_risk = create_new_risk_field(0)
    new_risk_fields.append(initial_risk)
    new_risk_factors_container.controls.append(initial_risk)
    
    initial_opp = create_new_opp_field(0)
    new_opp_fields.append(initial_opp)
    new_opportunities_container.controls.append(initial_opp)
    
    # Add buttons to add more fields
    add_new_risk_button = ft.ElevatedButton(
        "+ Agregar Factor de Riesgo",
        on_click=add_new_risk_field,
        bgcolor="#E53E3E",
        color=ft.Colors.WHITE,
        height=35,
        width=200
    )
    
    add_new_opp_button = ft.ElevatedButton(
        "+ Agregar Oportunidad",
        on_click=add_new_opp_field,
        bgcolor="#00BFA5",
        color=ft.Colors.WHITE,
        height=35,
        width=200
    )
    
    new_risk_factors_container.controls.append(add_new_risk_button)
    new_opportunities_container.controls.append(add_new_opp_button)
    
    # Error message
    error_text = ft.Text(
        "",
        color="#E53E3E",
        visible=False,
        size=12
    )

    # Validation function
    def validate_form():
        required_fields = [
            (project_name_field, "Nombre del Proyecto"),
            (customer_name_field, "Nombre del Cliente"),
            (customer_contact_field, "Contacto del Cliente"),
            (customer_email_field, "Email del Cliente"),
            (description_field, "Descripción del Proyecto"),
            (volume_field, "Volumen Esperado"),
            (price_field, "Precio Objetivo"),
            (delivery_field, "Fecha de Entrega"),
            (priority_dropdown, "Prioridad")
        ]
        
        missing_fields = []
        for field, label in required_fields:
            if not field.value or field.value.strip() == "":
                missing_fields.append(label)
        
        if missing_fields:
            error_text.value = f"Campos requeridos faltantes: {', '.join(missing_fields)}"
            error_text.visible = True
            page.update()
            return False
        
        # Validate email format
        if customer_email_field.value and "@" not in customer_email_field.value:
            error_text.value = "Formato de email inválido"
            error_text.visible = True
            page.update()
            return False
        
        # Validate numeric fields
        try:
            if price_field.value:
                float(price_field.value)
            if margin_field.value:
                float(margin_field.value)
        except ValueError:
            error_text.value = "Los campos de precio y margen deben ser números válidos"
            error_text.visible = True
            page.update()
            return False
        
        error_text.visible = False
        page.update()
        return True

    def save_project(e):
        if not validate_form():
            return
            
        try:
            # Calculate initial feasibility score based on form completeness
            completeness_score = 0
            total_fields = 15  # Total number of important fields
            
            if project_name_field.value: completeness_score += 1
            if customer_name_field.value: completeness_score += 1
            if customer_contact_field.value: completeness_score += 1
            if customer_email_field.value: completeness_score += 1
            if description_field.value: completeness_score += 1
            if volume_field.value: completeness_score += 1
            if price_field.value: completeness_score += 1
            if delivery_field.value: completeness_score += 1
            if tech_requirements_field.value: completeness_score += 1
            if quality_requirements_field.value: completeness_score += 1
            if regulatory_requirements_field.value: completeness_score += 1
            if dept1_dropdown.value: completeness_score += 1
            if new_risk_fields and new_risk_fields[0].value: completeness_score += 1
            if new_opp_fields and new_opp_fields[0].value: completeness_score += 1
            if priority_dropdown.value: completeness_score += 1
            
            initial_score = int((completeness_score / total_fields) * 100)
            
            new_project = ProjectInfo(
                id=0,  # Will be set by state
                project_name=project_name_field.value.strip(),
                customer_name=customer_name_field.value.strip(),
                customer_contact=customer_contact_field.value.strip(),
                customer_email=customer_email_field.value.strip(),
                customer_phone=customer_phone_field.value.strip() if customer_phone_field.value else "",
                project_description=description_field.value.strip(),
                expected_volume=volume_field.value.strip(),
                target_price=float(price_field.value) if price_field.value else 0.0,
                target_margin=float(margin_field.value) if margin_field.value else 0.0,
                delivery_date=delivery_field.value.strip(),
                technical_requirements=tech_requirements_field.value.strip() if tech_requirements_field.value else "",
                quality_requirements=quality_requirements_field.value.strip() if quality_requirements_field.value else "",
                regulatory_requirements=regulatory_requirements_field.value.strip() if regulatory_requirements_field.value else "",
                priority=priority_dropdown.value,
                status=ProjectStatus.NEW.value,
                created_by="Usuario del Sistema",
                created_date=datetime.datetime.now().strftime("%Y-%m-%d"),
                last_updated=datetime.datetime.now().strftime("%Y-%m-%d"),
                assigned_departments=[dept for dept in [dept1_dropdown.value, dept2_dropdown.value, dept3_dropdown.value] if dept],
                feasibility_score=initial_score,
                risk_factors=[risk.strip() for risk in [field.value for field in new_risk_fields] if risk and risk.strip()],
                opportunities=[opp.strip() for opp in [field.value for field in new_opp_fields] if opp and opp.strip()],
                comments=[],
                technical_drawings_pdf=pdf_files.copy(),
                technical_drawings_step=step_files.copy()
            )
            
            state.add_project(new_project)
            close_modal(modal, page)
            # Small delay to ensure modal is fully closed before refreshing
            import time
            time.sleep(0.1)
            update_dashboard(page)  # Refresh the dashboard after adding project
            
        except Exception as ex:
            error_text.value = f"Error al guardar el proyecto: {str(ex)}"
            error_text.visible = True
            page.update()

    def clear_form(e):
        # Clear all fields
        for field in [project_name_field, customer_name_field, customer_contact_field, 
                     customer_email_field, customer_phone_field, description_field,
                     volume_field, price_field, margin_field, delivery_field,
                     tech_requirements_field, quality_requirements_field, 
                     regulatory_requirements_field]:
            field.value = ""
        
        # Clear dynamic fields
        for field in new_risk_fields:
            field.value = ""
        for field in new_opp_fields:
            field.value = ""
        
        # Clear document lists
        pdf_files.clear()
        step_files.clear()
        update_document_display()
        
        for dropdown in [priority_dropdown, dept1_dropdown, dept2_dropdown, dept3_dropdown]:
            dropdown.value = None
        
        error_text.visible = False
        page.update()

    # Create tabbed interface for better organization
    basic_info_tab = ft.Column([
        ft.Text("Información Básica del Proyecto", size=16, weight="bold", color="#4A90E2"),
        ft.Row([
            ft.Column([
                project_name_field,
                customer_name_field,
                customer_contact_field,
                customer_email_field,
                customer_phone_field,
                customer_address_field,
                customer_website_field
            ], expand=True),
            ft.Column([
                description_field,
                project_type_dropdown,
                priority_dropdown
            ], expand=True)
        ])
    ], scroll=ft.ScrollMode.AUTO)
    
    commercial_tab = ft.Column([
        ft.Text("Información Comercial", size=16, weight="bold", color="#00BFA5"),
        ft.Row([
            ft.Column([
                volume_field,
                price_field,
                margin_field,
                delivery_field
            ], expand=True),
            ft.Column([
                contract_duration_field,
                payment_terms_field
            ], expand=True)
        ])
    ], scroll=ft.ScrollMode.AUTO)
    
    technical_tab = ft.Column([
        ft.Text("Requisitos Técnicos y de Calidad", size=16, weight="bold", color="#F5A623"),
        ft.Row([
            ft.Column([
                tech_requirements_field,
                quality_requirements_field
            ], expand=True),
            ft.Column([
                regulatory_requirements_field
            ], expand=True)
        ]),
        ft.Divider(),
        ft.Text("Documentos Técnicos", size=16, weight="bold", color="#4A90E2"),
        ft.Row([
            ft.Column([
                ft.Text("Planos 2D (PDF)", size=14, weight="bold"),
                ft.ElevatedButton(
                    "Seleccionar PDFs",
                    icon=ft.Icons.PICTURE_AS_PDF,
                    on_click=lambda e: pdf_picker.pick_files(
                        dialog_title="Seleccionar archivos PDF",
                        allow_multiple=True
                    ),
                    bgcolor="#E53E3E",
                    color=ft.Colors.WHITE,
                    width=200
                ),
                pdf_display
            ], expand=True),
            ft.Column([
                ft.Text("Modelos 3D (STEP)", size=14, weight="bold"),
                ft.ElevatedButton(
                    "Seleccionar STEP",
                    icon=ft.Icons.ENGINEERING,
                    on_click=lambda e: step_picker.pick_files(
                        dialog_title="Seleccionar archivos STEP",
                        allow_multiple=True
                    ),
                    bgcolor="#4A90E2",
                    color=ft.Colors.WHITE,
                    width=200
                ),
                step_display
            ], expand=True)
        ])
    ], scroll=ft.ScrollMode.AUTO)
    
    team_tab = ft.Column([
        ft.Text("Asignación de Equipos y Evaluación", size=16, weight="bold", color=ft.Colors.PURPLE),
        ft.Row([
            ft.Column([
                ft.Text("Departamentos Asignados", size=14, weight="bold"),
                dept1_dropdown,
                dept2_dropdown,
                dept3_dropdown
            ], expand=True),
            ft.Column([
                ft.Text("Factores de Riesgo", size=14, weight="bold"),
                new_risk_factors_container
            ], expand=True),
            ft.Column([
                ft.Text("Oportunidades", size=14, weight="bold"),
                new_opportunities_container
            ], expand=True)
        ])
    ], scroll=ft.ScrollMode.AUTO)

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Información Básica",
                icon=ft.Icons.INFO,
                content=basic_info_tab
            ),
            ft.Tab(
                text="Información Comercial",
                icon=ft.Icons.ATTACH_MONEY,
                content=commercial_tab
            ),
            ft.Tab(
                text="Requisitos Técnicos",
                icon=ft.Icons.ENGINEERING,
                content=technical_tab
            ),
            ft.Tab(
                text="Equipos y Evaluación",
                icon=ft.Icons.GROUP,
                content=team_tab
            )
        ],
        expand=True
    )

    # Create a custom modal using Container for better control
    modal = ft.Container(
        content=None,  # Will be set below
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
        padding=20,
        width=900,
        height=800,
        shadow=ft.BoxShadow(blur_radius=20, spread_radius=5, color=ft.Colors.BLACK26),
        visible=True
    )

    # Create buttons first for testing
    cancel_button = ft.ElevatedButton(
        "Cancelar",
        icon=ft.Icons.CANCEL,
        on_click=lambda e: close_modal(modal, page),
        bgcolor=ft.Colors.GREY_400,
        color=ft.Colors.WHITE,
        height=50,
        width=150
    )
    
    save_button = ft.ElevatedButton(
        "Guardar Proyecto",
        icon=ft.Icons.SAVE,
        bgcolor="#4A90E2",
        color=ft.Colors.WHITE,
        on_click=save_project,
        height=50,
        width=200
    )
    
    # Create scrollable content (without buttons)
    scrollable_content = ft.Column([
        error_text,
        tabs
    ], scroll=ft.ScrollMode.AUTO, expand=True)
    
    # Create modal content with fixed buttons at bottom
    modal_content = ft.Column([
        scrollable_content,
        ft.Divider(),
        ft.Container(
            content=ft.Row([
                cancel_button,
                save_button
            ], alignment=ft.MainAxisAlignment.END, spacing=10),
            bgcolor=ft.Colors.GREY_100,
            padding=10,
            border_radius=5
        )
    ], expand=True)

    # Update modal content
    modal.content = ft.Column([
        # Modal header
        ft.Row([
            ft.Text("Nuevo Proyecto de Factibilidad", size=18, weight="bold", expand=True),
            ft.IconButton(
                ft.Icons.CLOSE,
                on_click=lambda e: close_modal(modal, page),
                tooltip="Cerrar"
            )
        ]),
        ft.Divider(),
        # Modal content
        modal_content
    ], expand=True)
    
    # Create overlay background
    overlay = ft.Container(
        content=modal,
        bgcolor=ft.Colors.BLACK26,
        alignment=ft.alignment.center,
        expand=True,
        visible=True,
        on_click=lambda e: close_modal(modal, page) if e.target == overlay else None
    )
    
    # Set global reference and add to overlay
    current_modal = overlay
    page.overlay.append(overlay)
    
    # Debug output
    print(f"Modal created with height: {modal.height}")
    print(f"Modal content has {len(modal_content.controls)} controls")
    print(f"Scrollable content has {len(scrollable_content.controls)} controls")
    print(f"Buttons created: Cancel={cancel_button.text}, Save={save_button.text}")
    print(f"Cancel button visible: {cancel_button.visible}, Save button visible: {save_button.visible}")
    
    page.update()


def update_dashboard(page: ft.Page):
    """Refresh the dashboard after modal operations"""
    global project_list_ref, stats_row_ref
    try:
        # Update project list if reference exists
        if project_list_ref is not None:
            project_list_ref.controls.clear()
            projects = state.get_projects()
            project_list_ref.controls.extend([create_project_card(p, page) for p in projects])
        
        # Update statistics if reference exists
        if stats_row_ref is not None:
            # Recalculate statistics
            total = len(state.projects)
            feasible = len([p for p in state.projects if p.status == ProjectStatus.FEASIBLE.value])
            under_review = len([p for p in state.projects if p.status == ProjectStatus.UNDER_REVIEW.value])
            approved = len([p for p in state.projects if p.status == ProjectStatus.APPROVED.value])
            rejected = len([p for p in state.projects if p.status == ProjectStatus.REJECTED.value])
            not_feasible = len([p for p in state.projects if p.status == ProjectStatus.NOT_FEASIBLE.value])
            avg_score = sum(p.feasibility_score for p in state.projects) / total if total > 0 else 0
            
            # Update the statistics containers
            if len(stats_row_ref.controls) >= 7:
                # Update total projects
                total_container = stats_row_ref.controls[0]
                if hasattr(total_container, 'content') and hasattr(total_container.content, 'controls'):
                    total_container.content.controls[1].value = str(total)
                
                # Update feasible projects
                feasible_container = stats_row_ref.controls[1]
                if hasattr(feasible_container, 'content') and hasattr(feasible_container.content, 'controls'):
                    feasible_container.content.controls[1].value = str(feasible)
                
                # Update under review
                review_container = stats_row_ref.controls[2]
                if hasattr(review_container, 'content') and hasattr(review_container.content, 'controls'):
                    review_container.content.controls[1].value = str(under_review)
                
                # Update average score
                score_container = stats_row_ref.controls[3]
                if hasattr(score_container, 'content') and hasattr(score_container.content, 'controls'):
                    score_container.content.controls[1].value = f"{avg_score:.1f}%"
                
                # Update approved projects
                approved_container = stats_row_ref.controls[4]
                if hasattr(approved_container, 'content') and hasattr(approved_container.content, 'controls'):
                    approved_container.content.controls[1].value = str(approved)
                
                # Update rejected projects
                rejected_container = stats_row_ref.controls[5]
                if hasattr(rejected_container, 'content') and hasattr(rejected_container.content, 'controls'):
                    rejected_container.content.controls[1].value = str(rejected)
                
                # Update not feasible projects
                not_feasible_container = stats_row_ref.controls[6]
                if hasattr(not_feasible_container, 'content') and hasattr(not_feasible_container.content, 'controls'):
                    not_feasible_container.content.controls[1].value = str(not_feasible)
        
        # Force a complete page refresh to ensure all components are updated
        page.update()
    except Exception as e:
        print(f"Error updating dashboard: {e}")
        # Fallback: just update the page
        page.update()


def main(page: ft.Page):
    page.title = "Portal de Factibilidad"
    page.bgcolor = "#F8F9FA"  # Light grey background
    page.horizontal_alignment = "stretch"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Add keyboard event handler to close modals with Escape key
    def on_keyboard(e: ft.KeyboardEvent):
        if e.key == "Escape":
            force_close_all_modals(page)
    
    page.on_keyboard_event = on_keyboard

    # Header
    header = ft.Row(
        alignment="start",
        controls=[
            ft.Row([
                ft.Icon(ft.Icons.ASSESSMENT, color="#4A90E2", size=24),
                ft.Text("Portal de Factibilidad", size=20, weight="bold", color="#4A90E2")
            ])
        ]
    )

    # Filters and search
    def update_filters(e):
        state.filter_status = status_filter.value
        state.filter_priority = priority_filter.value
        state.search_term = search_field.value
        update_project_list()
        page.update()

    status_filter = ft.Dropdown(
        label="Filtrar por Estado",
        value=state.filter_status,
        options=[ft.dropdown.Option("Todos")] + [ft.dropdown.Option(s.value) for s in ProjectStatus],
        on_change=update_filters,
        width=200
    )

    priority_filter = ft.Dropdown(
        label="Filtrar por Prioridad",
        value=state.filter_priority,
        options=[ft.dropdown.Option("Todas")] + [ft.dropdown.Option(p.value) for p in Priority],
        on_change=update_filters,
        width=200
    )

    search_field = ft.TextField(
        label="Buscar proyecto o cliente",
        on_change=update_filters,
        prefix_icon=ft.Icons.SEARCH,
        width=300
    )

    # Project list
    project_list = ft.Row([], wrap=True, spacing=10)
    
    # Set global reference for updates
    global project_list_ref
    project_list_ref = project_list

    def update_project_list():
        project_list.controls.clear()
        projects = state.get_projects()
        project_list.controls.extend([create_project_card(p, page) for p in projects])

    # Statistics
    def get_stats():
        total = len(state.projects)
        feasible = len([p for p in state.projects if p.status == ProjectStatus.FEASIBLE.value])
        under_review = len([p for p in state.projects if p.status == ProjectStatus.UNDER_REVIEW.value])
        approved = len([p for p in state.projects if p.status == ProjectStatus.APPROVED.value])
        rejected = len([p for p in state.projects if p.status == ProjectStatus.REJECTED.value])
        not_feasible = len([p for p in state.projects if p.status == ProjectStatus.NOT_FEASIBLE.value])
        avg_score = sum(p.feasibility_score for p in state.projects) / total if total > 0 else 0
        
        return {
            "total": total,
            "feasible": feasible,
            "under_review": under_review,
            "approved": approved,
            "rejected": rejected,
            "not_feasible": not_feasible,
            "avg_score": avg_score
        }

    stats = get_stats()
    stats_row = ft.Row([
        ft.Container(
            content=ft.Column([
                ft.Text("Total Proyectos", size=14, weight="bold"),
                ft.Text(str(stats["total"]), size=24, color="#4A90E2")
            ], horizontal_alignment="center"),
            bgcolor=ft.Colors.WHITE,
            padding=15,
            border_radius=10,
            expand=True
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("Factibles", size=14, weight="bold"),
                ft.Text(str(stats["feasible"]), size=24, color="#00BFA5")
            ], horizontal_alignment="center"),
            bgcolor=ft.Colors.WHITE,
            padding=15,
            border_radius=10,
            expand=True
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("En Revisión", size=14, weight="bold"),
                ft.Text(str(stats["under_review"]), size=24, color="#F5A623")
            ], horizontal_alignment="center"),
            bgcolor=ft.Colors.WHITE,
            padding=15,
            border_radius=10,
            expand=True
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("Score Promedio", size=14, weight="bold"),
                ft.Text(f"{stats['avg_score']:.1f}%", size=24, color="#00BFA5")
            ], horizontal_alignment="center"),
            bgcolor=ft.Colors.WHITE,
            padding=15,
            border_radius=10,
            expand=True
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("Aprobados", size=14, weight="bold"),
                ft.Text(str(stats["approved"]), size=24, color="#00BFA5")
            ], horizontal_alignment="center"),
            bgcolor=ft.Colors.WHITE,
            padding=15,
            border_radius=10,
            expand=True
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("Rechazados", size=14, weight="bold"),
                ft.Text(str(stats["rejected"]), size=24, color="#E53E3E")
            ], horizontal_alignment="center"),
            bgcolor=ft.Colors.WHITE,
            padding=15,
            border_radius=10,
            expand=True
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("No Factibles", size=14, weight="bold"),
                ft.Text(str(stats["not_feasible"]), size=24, color="#E53E3E")
            ], horizontal_alignment="center"),
            bgcolor=ft.Colors.WHITE,
            padding=15,
            border_radius=10,
            expand=True
        )
    ])
    
    # Set global reference for statistics updates
    global stats_row_ref
    stats_row_ref = stats_row

    # Main layout
    page.add(
        ft.Column([
            header,
            ft.Divider(),
            
            # Controls
            ft.Row([
                ft.ElevatedButton(
                    "+ Nuevo Proyecto",
                    bgcolor="#4A90E2",
                    color=ft.Colors.WHITE,
                    on_click=lambda e: create_new_project_form(page)
                ),
                status_filter,
                priority_filter,
                search_field
            ], alignment="spaceBetween"),
            
            ft.Divider(),
            
            # Statistics
            stats_row,
            
            ft.Divider(),
            
            # Project list
            ft.Text("Proyectos de Factibilidad", size=18, weight="bold"),
            project_list
        ])
    )

    # Initialize project list
    update_project_list()
    page.update()

if __name__ == "__main__":
    ft.app(main)
