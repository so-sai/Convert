# SPEC: Task 7.1 - Search UI with SvelteKit

> **Sprint:** 7 - Frontend & Search UI  
> **Status:** DRAFT  
> **Created:** 2025-12-28  
> **Dependencies:** Sprint 6 (SQLCipher FTS5 indexer)

---

## 1. OBJECTIVE

Build a **real-time search interface** using SvelteKit 2.0 that queries the encrypted FTS5 database created by Sprint 6's background services.

**Success Criteria:**
- Search latency < 50ms (keystroke → results)
- Preview load < 100ms (click → content display)
- 60fps UI responsiveness
- Bundle size < 500KB (gzipped)

---

## 2. ARCHITECTURE

### 2.1 Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | SvelteKit | 2.0+ |
| **Styling** | Tailwind CSS | 3.4+ |
| **Build Tool** | Vite | 5.0+ |
| **Backend API** | FastAPI | 0.109+ |
| **Database** | SQLCipher | 4.5+ |

### 2.2 Component Structure

```
src/
├── routes/
│   ├── +page.svelte          # Main search interface
│   └── api/
│       ├── search/+server.ts # Search endpoint proxy
│       └── preview/+server.ts # Preview endpoint proxy
├── lib/
│   ├── components/
│   │   ├── SearchBar.svelte
│   │   ├── ResultsList.svelte
│   │   ├── FilePreview.svelte
│   │   └── FilterPanel.svelte
│   ├── stores/
│   │   └── searchStore.ts    # Reactive search state
│   └── api/
│       └── client.ts          # API client utilities
└── app.css                    # Tailwind + custom styles
```

---

## 3. BACKEND API SPECIFICATION

### 3.1 Search Endpoint

**URL:** `GET /api/search`

**Query Parameters:**
```typescript
interface SearchParams {
  q: string;           // Search query
  limit?: number;      // Max results (default: 20)
  file_type?: string;  // Filter: 'pdf' | 'docx' | 'all'
  offset?: number;     // Pagination offset
}
```

**Response:**
```typescript
interface SearchResponse {
  results: Array<{
    file_id: string;
    file_path: string;
    file_type: string;
    snippet: string;      // Highlighted excerpt
    rank: number;         // FTS5 relevance score
    modified_at: string;  // ISO timestamp
  }>;
  total: number;
  query_time_ms: number;
}
```

### 3.2 Preview Endpoint

**URL:** `GET /api/preview/{file_id}`

**Response:**
```typescript
interface PreviewResponse {
  file_id: string;
  file_name: string;
  content: string;      // First 500 chars
  full_length: number;  // Total chars
}
```

---

## 4. UI/UX REQUIREMENTS

### 4.1 Search Bar
- **Instant Search:** Debounce 150ms, trigger on keystroke
- **Clear Button:** Reset search state
- **Loading Indicator:** Show during API call

### 4.2 Results List
- **Highlight:** Match terms in snippets
- **Metadata:** Show file type icon, modified date
- **Click Action:** Load preview in side panel

### 4.3 File Preview
- **Side Panel:** Slide-in animation (300ms)
- **Content:** Scrollable, syntax-highlighted if code
- **Actions:** "Open in Explorer", "Copy Path"

### 4.4 Filter Panel
- **File Type:** Checkboxes for PDF, DOCX
- **Date Range:** Optional date picker
- **Sort:** Relevance, Date (newest/oldest)

### 4.5 Dark/Light Mode
- **Toggle:** Persistent in localStorage
- **Colors:** Follow system preference by default

---

## 5. IMPLEMENTATION PLAN

### Phase 1: Backend API (2 hours)
1. Create FastAPI endpoints in `app.py`
2. Implement FTS5 search query with highlighting
3. Add preview extraction logic
4. Test with curl/Postman

### Phase 2: SvelteKit Setup (1 hour)
1. Initialize SvelteKit project: `npm create svelte@latest`
2. Install dependencies: Tailwind, TypeScript
3. Configure Vite for API proxy

### Phase 3: Core Components (3 hours)
1. Build `SearchBar.svelte` with debouncing
2. Build `ResultsList.svelte` with virtual scrolling
3. Build `FilePreview.svelte` with lazy loading
4. Integrate with search store

### Phase 4: Styling & Polish (2 hours)
1. Apply Tailwind dark mode
2. Add animations (Svelte transitions)
3. Optimize bundle size

### Phase 5: Testing (1 hour)
1. Manual testing with real data
2. Performance profiling (Chrome DevTools)
3. Accessibility audit (Lighthouse)

---

## 6. ACCEPTANCE TESTS

### T71.01: Search Latency
```python
def test_search_latency():
    """Search results appear within 50ms"""
    start = time.perf_counter()
    response = client.get("/api/search?q=test")
    elapsed = (time.perf_counter() - start) * 1000
    assert elapsed < 50
    assert response.status_code == 200
```

### T71.02: Preview Load
```python
def test_preview_load():
    """Preview loads within 100ms"""
    file_id = "test-file-123"
    start = time.perf_counter()
    response = client.get(f"/api/preview/{file_id}")
    elapsed = (time.perf_counter() - start) * 1000
    assert elapsed < 100
    assert "content" in response.json()
```

### T71.03: Highlight Accuracy
```typescript
test('highlights search terms', async () => {
  const results = await searchAPI.search('python');
  results.forEach(r => {
    expect(r.snippet).toContain('<mark>python</mark>');
  });
});
```

### T71.04: Filter Functionality
```typescript
test('filters by file type', async () => {
  const results = await searchAPI.search('test', { file_type: 'pdf' });
  results.forEach(r => {
    expect(r.file_type).toBe('pdf');
  });
});
```

---

## 7. PERFORMANCE TARGETS

| Metric | Target | Measurement |
|--------|--------|-------------|
| **First Contentful Paint** | < 1s | Lighthouse |
| **Time to Interactive** | < 2s | Lighthouse |
| **Search API Latency** | < 50ms | Backend logs |
| **Preview API Latency** | < 100ms | Backend logs |
| **Bundle Size (gzipped)** | < 500KB | `vite build --report` |
| **Lighthouse Score** | > 90 | Chrome DevTools |

---

## 8. SECURITY CONSIDERATIONS

1. **Input Sanitization:** Escape user queries to prevent SQL injection
2. **Path Traversal:** Validate file_id to prevent directory traversal
3. **Rate Limiting:** Max 100 requests/minute per IP
4. **CORS:** Restrict to localhost during development

---

## 9. FUTURE ENHANCEMENTS (Sprint 8+)

- [ ] Advanced filters (size, extension, tags)
- [ ] Search history with autocomplete
- [ ] Export results to CSV
- [ ] Keyboard shortcuts (Cmd+K to focus search)
- [ ] Real-time updates via WebSocket

---

**Status:** Ready for implementation  
**Estimated Effort:** 9 hours  
**Target Completion:** 2025-12-28 EOD
