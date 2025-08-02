# TASK: Build Propter-Optimis Sports Analytics Platform

## Objective: Create a full-stack sports analytics application that integrates with existing Webflow landing page and reduces analysis time from 4+ hours to 15 minutes using AI-powered analysis.

## Important Notes:
- **NOT building a landing page** - Webflow site exists at https://www.propter-optimis.pro/
- **Building APPLICATION interface only** - for authenticated users post-signup
- **Must match purple branding (#7c3aed)** from existing Webflow site
- **Professional B2B SaaS** targeting sports analysts and coaches
- **Cross-domain integration** required for seamless user flow

## STEPs:

[✅] STEP 1: Setup Supabase authentication for full-stack application with PostgreSQL database -> System STEP

[✅] STEP 2: Build the complete full-stack sports analytics application with:
   - Django REST Framework backend with OpenStar Lab integration
   - React SPA frontend (application interface only)
   - Professional analytics dashboard for sports analysts
   - Video upload and AI-powered analysis pipeline
   - Export functionality and manual annotation capabilities
   - Brand consistency with existing Webflow landing page
   -> Web Development STEP

**APPLICATION DEPLOYED:** https://oa7xpghbln83.space.minimax.io

[ ] STEP 3: Create comprehensive documentation including README, API docs, deployment guides, and development setup instructions -> Documentation STEP

## Technical Architecture:
- **Backend**: Django REST Framework + PostgreSQL
- **Frontend**: React SPA (professional analytics interface)
- **ML Integration**: OpenStar Lab packages for AI analysis
- **Authentication**: JWT with cross-domain support
- **Storage**: File system → AWS S3 migration path
- **Deployment**: Railway/Render (backend) + Vercel/Netlify (frontend)

## Core Features:
1. User authentication (login/signup/password reset)
2. Video upload interface (drag-and-drop, 2GB files)
3. Analysis intent selection (5 specific options)
4. AI processing pipeline (15-minute analysis)
5. Professional analytics dashboard with visualizations
6. Export functionality (video clips, PDFs, CSV)
7. Manual annotation capabilities
8. Team management features

## Success Criteria:
- 87% reduction in analysis time (4 hours → 30 minutes)
- 95% reduction in report generation time
- Professional-grade UI matching Webflow branding
- Seamless integration with existing landing page
- >80% test coverage with comprehensive documentation

## Deliverable: Complete working full-stack sports analytics application with deployment scripts and documentation.