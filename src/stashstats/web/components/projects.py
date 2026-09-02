"""UI component factories for the Projects tab PDF management UI."""

from typing import Any

import dash_bootstrap_components as dbc
from dash import dcc, html


def create_pdf_file_list(
    filenames: list[str],
    project_id: str | int,
    user_id: str | int,
) -> list[Any]:
    """Render the list of attached PDFs for a project.

    Each file entry shows a clickable filename button (opens inline viewer) and
    a delete button. Returns an empty-state message when no files exist.

    Args:
        filenames: Sorted list of PDF filenames attached to the project.
        project_id: Project identifier used to scope button IDs.
        user_id: User identifier (not used in ID but kept for future use).

    Returns:
        list of Dash component children suitable for a ``children`` prop.
    """
    if not filenames:
        return [html.P("No PDFs attached.", className="text-muted small mb-0")]

    rows: list[Any] = []
    for fname in filenames:
        row = dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        fname,
                        id={"type": "project-pdf-view-btn", "index": str(project_id), "filename": fname},
                        color="link",
                        size="sm",
                        className="text-start p-0",
                        n_clicks=0,
                    ),
                    width="auto",
                    className="me-auto",
                ),
                dbc.Col(
                    dbc.Button(
                        html.I(className="bi bi-trash"),
                        id={"type": "project-pdf-delete-btn", "index": str(project_id), "filename": fname},
                        color="danger",
                        size="sm",
                        outline=True,
                        n_clicks=0,
                        title=f"Delete {fname}",
                    ),
                    width="auto",
                ),
            ],
            className="align-items-center mb-1 g-1",
        )
        rows.append(row)
    return rows


def create_pdf_viewer(project_id: str | int, src_url: str = "") -> html.Iframe:
    """Render an inline PDF viewer iframe.

    Args:
        project_id: Project identifier used to scope the component ID.
        src_url: Initial src URL for the iframe (empty string = blank).

    Returns:
        ``html.Iframe`` configured for PDF display.
    """
    return html.Iframe(
        id={"type": "project-pdf-viewer", "index": str(project_id)},
        src=src_url,
        style={
            "width": "100%",
            "height": "600px",
            "border": "1px solid #444",
            "borderRadius": "4px",
            "backgroundColor": "#1a1a1a",
            "display": "block" if src_url else "none",
        },
    )


def create_pdf_upload_zone(project_id: str | int) -> dcc.Upload:
    """Render the dcc.Upload dropzone for a project.

    Accepts only PDF files; multiple uploads allowed.

    Args:
        project_id: Project identifier used to scope the component ID.

    Returns:
        Configured ``dcc.Upload`` component.
    """
    return dcc.Upload(
        id={"type": "project-pdf-upload", "index": str(project_id)},
        accept=".pdf,application/pdf",
        multiple=False,  # one at a time; re-trigger for each file
        children=html.Div(
            [
                html.I(className="bi bi-file-earmark-pdf me-2"),
                "Drag & drop a PDF or ",
                html.A("click to upload", href="#"),
            ],
            className="text-center text-muted py-2 small",
        ),
        style={
            "border": "2px dashed #555",
            "borderRadius": "6px",
            "padding": "8px",
            "cursor": "pointer",
        },
    )

import math

def filter_projects(projects: list[dict[str, Any]], search_query: str) -> list[dict[str, Any]]:
    """Filter projects based on a case-insensitive text search.
    
    Matches against project name, pattern name, craft name, status name, and tags.
    """
    if not search_query:
        return projects
        
    query = search_query.lower().strip()
    filtered = []
    for proj in projects:
        name = str(proj.get("name") or "").lower()
        pattern = str(proj.get("pattern_name") or "").lower()
        craft = str(proj.get("craft_name") or "").lower()
        status = str(proj.get("status_name") or "").lower()
        tags = [str(t).lower() for t in proj.get("tag_names") or []]
        
        if (query in name or 
            query in pattern or 
            query in craft or 
            query in status or 
            any(query in t for t in tags)):
            filtered.append(proj)
            
    return filtered

def sort_projects(projects: list[dict[str, Any]], sort_by: str) -> list[dict[str, Any]]:
    """Sort projects based on the selected option."""
    if sort_by == "name_asc":
        return sorted(projects, key=lambda p: str(p.get("name") or "").lower())
    elif sort_by == "progress_desc":
        return sorted(projects, key=lambda p: float(p.get("progress") or 0.0), reverse=True)
    elif sort_by == "status_asc":
        return sorted(projects, key=lambda p: str(p.get("status_name") or "").lower())
    else:
        # Default to date_desc (started or created_at)
        def _get_date(p: dict[str, Any]) -> str:
            started = p.get("started")
            if started:
                return str(started)
            return str(p.get("created_at") or "")
            
        return sorted(projects, key=_get_date, reverse=True)

def paginate_projects(projects: list[dict[str, Any]], page: int, page_size: int = 10) -> tuple[int, list[dict[str, Any]]]:
    """Paginate a list of projects, ensuring the active page is clamped to valid bounds."""
    if not projects:
        return 1, []
        
    total_pages = math.ceil(len(projects) / page_size)
    
    # Clamp page to [1, total_pages]
    active_page = max(1, min(page, total_pages))
    
    start_idx = (active_page - 1) * page_size
    end_idx = start_idx + page_size
    
    return active_page, projects[start_idx:end_idx]

def create_project_accordion_item(project: dict[str, Any], user_id: str | int = "default") -> dbc.AccordionItem:
    """Render a single project as an accordion item."""
    project_id = project.get("id") or "0"
    name = project.get("name") or "Unnamed Project"
    pattern = project.get("pattern_name") or ""
    
    # Title building
    title_text = f"{name} — {pattern}" if pattern else name
    
    # Badges
    badges = []
    status_name = project.get("status_name")
    if status_name:
        status_color = "secondary"
        if status_name.lower() == "finished":
            status_color = "success"
        elif status_name.lower() == "in progress":
            status_color = "primary"
        elif status_name.lower() == "frogged":
            status_color = "danger"
            
        badges.append(
            dbc.Badge(status_name, color=status_color, className="ms-2")
        )
        
    progress = project.get("progress")
    if progress is not None:
        badges.append(
            dbc.Badge(f"{progress}%", color="info", className="ms-1")
        )
        
    # Header
    header_content = html.Div(
        [
            html.Span(title_text, className="fw-semibold"),
            html.Div(badges, className="d-inline-block"),
        ],
        className="d-flex align-items-center justify-content-between w-100"
    )
    
    # Body
    craft_name = project.get("craft_name") or "Unknown"
    started = project.get("started")
    completed = project.get("completed")
    
    metadata = html.Div(
        [
            html.Span(f"Craft: {craft_name}", className="me-3 text-muted small"),
            html.Span(f"Started: {started}" if started else "", className="me-3 text-muted small"),
            html.Span(f"Finished: {completed}" if completed else "", className="me-3 text-muted small"),
        ],
        className="mb-3"
    )
    
    progress_bar = dbc.Progress(
        value=progress or 0, 
        color="info", 
        striped=True, 
        className="mb-3"
    )
    
    existing_pdfs = project.get("existing_pdfs")
    if existing_pdfs is None:
        user_id = project.get("user_id", user_id)
        from stashstats.storage import list_project_pdfs, DEFAULT_DATA_DIR
        existing_pdfs = list_project_pdfs(user_id, str(project_id), base_dir=DEFAULT_DATA_DIR)
    
    pdf_section = html.Div(
        [
            html.H6("PDF Attachments", className="mb-2"),
            create_pdf_upload_zone(project_id),
            html.Div(id={"type": "project-pdf-error", "index": str(project_id)}, className="text-danger small mt-1"),
            html.Div(create_pdf_file_list(existing_pdfs, project_id, user_id), id={"type": "project-pdf-list", "index": str(project_id)}),
            create_pdf_viewer(project_id),
        ]
    )
    
    return dbc.AccordionItem(
        children=[metadata, progress_bar, pdf_section],
        title=header_content,
        item_id=f"project-{project_id}",
    )


def create_grouped_projects_accordion(projects: list[dict[str, Any]], user_id: str | int = "default") -> Any:
    """Wrap a list of projects into an accordion layout."""
    if not projects:
        return html.Div(
            dbc.Alert(
                "No projects found matching the criteria.",
                color="info",
                className="mt-3 text-center",
            )
        )
        
    items = []
    for p in projects:
        items.append(create_project_accordion_item(p, user_id=user_id))
        
    return dbc.Accordion(
        items,
        start_collapsed=True,
        always_open=True,
        id="projects-accordion",
        className="mt-3",
    )
