# Phase 3: Frontend

> React dashboard with all major user-facing features

**Target**: Week 5-6
**Status**: Not Started
**Tasks**: 10
**Depends On**: Phase 2

---

## Objectives

1. Set up React project with TypeScript
2. Implement authentication UI
3. Build dashboard overview
4. Create transaction management views
5. Implement debt tracking visualization
6. Build chat/query interface
7. Ensure mobile responsiveness

---

## Task Breakdown

### U-001: React Project Setup

**Priority**: High | **Status**: ⬜ Not Started

Create React frontend with Vite:

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/          # shadcn/ui components
│   │   ├── layout/      # Layout components
│   │   └── features/    # Feature-specific components
│   ├── pages/
│   ├── hooks/
│   ├── services/        # API calls
│   ├── stores/          # Zustand stores
│   ├── types/
│   └── utils/
├── public/
├── package.json
└── vite.config.ts
```

**Stack**:
- React 18
- TypeScript 5
- Vite
- Tailwind CSS
- shadcn/ui
- Zustand
- React Router
- Axios

**Acceptance Criteria**:
- [ ] Vite + React project running
- [ ] TypeScript configured
- [ ] Tailwind CSS working
- [ ] shadcn/ui installed
- [ ] Folder structure established
- [ ] ESLint + Prettier configured

---

### U-002: Authentication Pages

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: U-001

Login and registration pages:

**Pages**:
- `/login` - User login
- `/register` - New account creation
- `/forgot-password` - Password recovery (optional for MVP)

**Features**:
- Form validation
- Error display
- Loading states
- Remember me option
- Redirect after login

**Acceptance Criteria**:
- [ ] Login page functional
- [ ] Registration page functional
- [ ] JWT stored securely
- [ ] Auto-redirect to dashboard
- [ ] Error messages displayed
- [ ] Mobile responsive

---

### U-003: Dashboard Overview

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: U-002

Main dashboard page:

**Components**:
- Monthly spending summary card
- Category breakdown chart (pie/bar)
- Recent transactions list (5-10)
- Debt summary card
- Upcoming predictions card
- Quick actions (upload, ask question)

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  Header (Logo, User menu)                                   │
├──────────┬──────────────────────────────────────────────────┤
│          │  Welcome, Ahmad                                  │
│  Sidebar │  ┌──────────────┐ ┌──────────────┐              │
│          │  │ Total Spent  │ │ Total Debt   │              │
│  - Dash  │  │   RM 3,450   │ │   RM 28,500  │              │
│  - Trans │  └──────────────┘ └──────────────┘              │
│  - Debts │                                                  │
│  - Chat  │  ┌────────────────────────────────────────────┐ │
│  - Upload│  │        Category Breakdown Chart            │ │
│          │  └────────────────────────────────────────────┘ │
│          │                                                  │
│          │  ┌────────────────────────────────────────────┐ │
│          │  │         Recent Transactions                │ │
│          │  └────────────────────────────────────────────┘ │
└──────────┴──────────────────────────────────────────────────┘
```

**Acceptance Criteria**:
- [ ] Dashboard loads with real data
- [ ] Summary cards display correctly
- [ ] Category chart renders
- [ ] Recent transactions list shows
- [ ] Mobile responsive layout
- [ ] Empty state for new users

---

### U-004: Transaction List

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: U-003

Full transaction management view:

**Features**:
- Paginated transaction list
- Search by description
- Filter by category
- Filter by date range
- Filter by amount range
- Sort by date/amount
- Transaction detail modal
- Edit category (manual override)

**Table Columns**:
- Date
- Description
- Category (with confidence indicator)
- Amount
- Source (bank/e-wallet)
- Actions

**Acceptance Criteria**:
- [ ] Transaction list loads with pagination
- [ ] All filters working
- [ ] Search working
- [ ] Sort working
- [ ] Transaction detail expandable
- [ ] Category edit possible
- [ ] Mobile: card layout instead of table

---

### U-005: Statement Upload Interface

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: U-003

Upload statement files:

**Features**:
- Drag and drop upload zone
- File type validation (PDF, CSV)
- Bank selection (or auto-detect)
- Upload progress indicator
- Processing status display
- Results summary

**Flow**:
```
Select File → Upload → Processing → Review → Confirm
```

**Acceptance Criteria**:
- [ ] Drag-drop upload working
- [ ] File validation working
- [ ] Progress indicator shows
- [ ] Processing status updates
- [ ] Results summary displayed
- [ ] Error handling for bad files

---

### U-006: Debt Tracker View

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: U-003

Tri-tier debt visualization:

**Components**:
- Total debt summary
- Debt by tier (FORMAL, BNPL, HUTANG)
- Individual debt cards
- Monthly obligation calculation
- Debt trend chart (optional)

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  Total Debt: RM 28,500                                      │
│  Monthly Obligation: RM 1,416                               │
├─────────────────────────────────────────────────────────────┤
│  FORMAL               BNPL                HUTANG            │
│  RM 27,500            RM 200              RM 800            │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ PTPTN        │    │ SPayLater    │    │ To: Ahmad    │  │
│  │ RM 25,000    │    │ RM 100       │    │ RM 800       │  │
│  │ RM 250/month │    │ 2/6 paid     │    │ Pending      │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│  ┌──────────────┐    ┌──────────────┐                      │
│  │ Car Loan     │    │ GrabPayLater │                      │
│  │ RM 2,500     │    │ RM 100       │                      │
│  │ RM 600/month │    │ 1/3 paid     │                      │
│  └──────────────┘    └──────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

**Acceptance Criteria**:
- [ ] Total debt displayed
- [ ] Breakdown by tier
- [ ] Individual debt cards
- [ ] Monthly obligation calculated
- [ ] Visual distinction between tiers
- [ ] Mobile responsive

---

### U-007: Pattern Visualization

**Priority**: Medium | **Status**: ⬜ Not Started | **Depends On**: U-003

Display discovered patterns:

**Pattern Cards**:
- Pattern name and description
- Evidence summary
- Impact (RM)
- Confidence level
- Pattern type icon/badge

**Visualizations**:
- Hidden costs breakdown (bar chart)
- Temporal patterns (heatmap or line)
- Trend arrows for categories

**Acceptance Criteria**:
- [ ] Pattern cards displayed
- [ ] Hidden costs chart
- [ ] Impact amounts shown
- [ ] Actionable insights highlighted
- [ ] Empty state if no patterns

---

### U-008: Chat/Query Interface

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: U-003

Conversational query interface:

**Features**:
- Chat input box
- Message history
- Structured data display in responses
- Charts/tables embedded in responses
- Follow-up question suggestions
- Loading indicator during processing

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  Ask about your finances                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  You: How much did I spend on food this month?              │
│                                                             │
│  RinggitSense: You spent RM 892.50 on food in January.     │
│                                                             │
│  [Bar Chart: Food spending by week]                         │
│                                                             │
│  Related questions:                                         │
│  • How does this compare to last month?                     │
│  • What's my daily food spending average?                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────┐  [Send]       │
│  │ Ask a question...                        │               │
│  └─────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

**Acceptance Criteria**:
- [ ] Chat input working
- [ ] Responses display correctly
- [ ] Data visualizations render
- [ ] Follow-up questions clickable
- [ ] Loading state shows
- [ ] Error messages display

---

### U-009: Advice Display

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: U-003

Financial advice with disclaimers:

**Components**:
- Advice cards sorted by priority
- Category badges
- Impact and difficulty indicators
- Action steps expandable
- **Disclaimer banner (REQUIRED)**

**Disclaimer Display**:
```
┌─────────────────────────────────────────────────────────────┐
│ ⚠️ Important Disclaimer                                     │
│ This is not professional financial advice. Consult a        │
│ licensed financial advisor for major decisions.             │
└─────────────────────────────────────────────────────────────┘
```

**Acceptance Criteria**:
- [ ] Disclaimer always visible
- [ ] Advice cards display
- [ ] Priority ordering correct
- [ ] Action steps expandable
- [ ] Impact/difficulty shown
- [ ] Culturally appropriate content

---

### U-010: Mobile Responsive Design

**Priority**: Medium | **Status**: ⬜ Not Started | **Depends On**: U-003 through U-009

Ensure all pages work on mobile:

**Breakpoints**:
- Mobile: <640px
- Tablet: 640px - 1024px
- Desktop: >1024px

**Mobile Adaptations**:
- Collapsible sidebar (hamburger menu)
- Stack cards vertically
- Transaction cards instead of table
- Touch-friendly inputs
- Smaller charts

**Acceptance Criteria**:
- [ ] All pages tested on mobile
- [ ] Navigation works on mobile
- [ ] Charts readable on mobile
- [ ] Touch targets appropriate size
- [ ] No horizontal scrolling

---

## Exit Criteria

Phase 3 is complete when:

1. ✅ All pages functional and connected to API
2. ✅ Authentication flow complete
3. ✅ Dashboard shows real data
4. ✅ Statement upload works
5. ✅ Chat interface operational
6. ✅ Mobile responsive
7. ✅ All U-xxx tasks marked Done

---

## Dependencies

| External | Internal |
|----------|----------|
| None | Phase 2 complete |

---

**Document Status**: Complete
**Last Updated**: 2026-01-10
