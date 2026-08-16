# Specification: Yarn Search Integration (Ravelry API)

## 1. Overview
Implement the "Yarn Search" tab in the StashStats web dashboard. This feature will connect to the Ravelry API to allow users to search the global yarn database, view details via an expanding accordion interface, and handle large result sets using traditional pagination.

## 2. Scope & Functional Requirements

### 2.1 Search Interface
- **Search Inputs**:
  - Keyword/Query text input field.
  - Brand/Yarn Company text input.
- **Trigger**: A "Search" button and trigger on "Enter" keypress.

### 2.2 Ravelry API Integration
- Connect the search inputs to the `RavelryClient` endpoint for yarn search.
- Retrieve and map the API response payload to populate the UI.

### 2.3 Presentation & Interaction
- **Results Layout**: Render results using an expanding accordion list.
- **Accordion Header**: Display the yarn name, brand, and a thumbnail image.
- **Accordion Body**: Expand details inline when clicked. Details should include fiber content, weight, yardage, and gauge (based on API availability).
- **Pagination**: Implement traditional Next/Prev page numbers to navigate through pages returned by the Ravelry API.

## 3. Out of Scope
- Searching for Patterns or Projects (limited to Yarn searches only for this track).
- Adding searched yarns directly to the user's Personal Stash (to be handled in a future track).
- Advanced filtering (e.g., fiber content, weight sliders) beyond Keyword and Brand.
