import { Link } from "react-router-dom";

import "./LandingPage.css";


const platformFeatures = [
    {
        icon: "◈",
        title: "Dataset Intelligence",
        description:
            "Upload, inspect, and prepare datasets through a structured machine-learning workflow.",
    },
    {
        icon: "⌘",
        title: "Automated Training",
        description:
            "Train and evaluate multiple machine-learning models from one unified workspace.",
    },
    {
        icon: "◎",
        title: "Experiment Tracking",
        description:
            "Track parameters, metrics, artifacts, and model performance with MLflow.",
    },
    {
        icon: "◉",
        title: "Model Registry",
        description:
            "Version, promote, manage, and organize trained models across deployment stages.",
    },
];


const workflowSteps = [
    {
        number: "01",
        title: "Upload Data",
        description:
            "Bring your dataset into a controlled machine-learning workspace.",
    },
    {
        number: "02",
        title: "Train Models",
        description:
            "Configure training and evaluate model performance automatically.",
    },
    {
        number: "03",
        title: "Track & Register",
        description:
            "Store experiments, metrics, artifacts, and model versions.",
    },
    {
        number: "04",
        title: "Predict",
        description:
            "Use production-ready models through a structured prediction API.",
    },
];


const platformStats = [
    {
        value: "End-to-End",
        label: "ML Workflow",
    },
    {
        value: "MLflow",
        label: "Experiment Tracking",
    },
    {
        value: "Versioned",
        label: "Model Registry",
    },
];


function LandingPage() {
    return (
        <main className="landing-page">

            {/* ==================================================
                Background Effects
            ================================================== */}

            <div
                className="landing-background"
                aria-hidden="true"
            >
                <div className="landing-orb landing-orb-one" />

                <div className="landing-orb landing-orb-two" />

                <div className="landing-grid" />
            </div>


            {/* ==================================================
                Navigation
            ================================================== */}

            <header className="landing-header">

                <nav
                    className="landing-navbar container"
                    aria-label="Main navigation"
                >

                    <Link
                        to="/"
                        className="landing-brand"
                    >

                        <span className="brand-mark">
                            DF
                        </span>

                        <span className="brand-name">
                            DataForge
                        </span>

                    </Link>


                    <div className="landing-nav-links">

                        <a href="#features">
                            Features
                        </a>

                        <a href="#workflow">
                            Workflow
                        </a>

                        <Link to="/dashboard">
                            Dashboard
                        </Link>

                    </div>


                    <Link
                        to="/dashboard"
                        className="nav-dashboard-button"
                    >
                        Open Platform

                        <span aria-hidden="true">
                            →
                        </span>

                    </Link>

                </nav>

            </header>


            {/* ==================================================
                Hero
            ================================================== */}

            <section className="hero-section">

                <div className="container hero-container">

                    <div className="hero-content">

                        <div className="hero-badge">

                            <span
                                className="status-dot"
                                aria-hidden="true"
                            />

                            Production-focused
                            MLOps platform

                        </div>


                        <h1 className="hero-title">

                            Build machine learning

                            <span>
                                with a complete workflow.
                            </span>

                        </h1>


                        <p className="hero-description">

                            DataForge brings dataset management,
                            automated model training, experiment
                            tracking, model versioning, and
                            prediction services into one
                            structured platform.

                        </p>


                        <div className="hero-actions">

                            <Link
                                to="/dashboard"
                                className="primary-button"
                            >

                                Launch Dashboard

                                <span aria-hidden="true">
                                    →
                                </span>

                            </Link>


                            <a
                                href="#workflow"
                                className="secondary-button"
                            >
                                Explore Workflow
                            </a>

                        </div>


                        <div className="hero-trust">

                            <span>
                                Built for AI projects
                            </span>

                            <span
                                aria-hidden="true"
                            >
                                •
                            </span>

                            <span>
                                Designed for MLOps
                            </span>

                            <span
                                aria-hidden="true"
                            >
                                •
                            </span>

                            <span>
                                Ready to scale
                            </span>

                        </div>

                    </div>


                    {/* ==========================================
                        Hero Dashboard Preview
                    ========================================== */}

                    <div className="hero-visual">

                        <div className="dashboard-preview">

                            <div className="preview-topbar">

                                <div className="preview-brand">

                                    <span className="preview-logo">
                                        DF
                                    </span>

                                    <div>

                                        <strong>
                                            DataForge
                                        </strong>

                                        <small>
                                            MLOps Workspace
                                        </small>

                                    </div>

                                </div>


                                <div className="preview-status">

                                    <span />

                                    System Online

                                </div>

                            </div>


                            <div className="preview-body">

                                <aside className="preview-sidebar">

                                    <span className="sidebar-active">
                                        Overview
                                    </span>

                                    <span>
                                        Datasets
                                    </span>

                                    <span>
                                        Training
                                    </span>

                                    <span>
                                        Experiments
                                    </span>

                                    <span>
                                        Models
                                    </span>

                                </aside>


                                <div className="preview-content">

                                    <div className="preview-heading">

                                        <div>

                                            <span>
                                                WORKSPACE
                                            </span>

                                            <h2>
                                                Model Overview
                                            </h2>

                                        </div>


                                        <button
                                            type="button"
                                        >
                                            + New Training
                                        </button>

                                    </div>


                                    <div className="metric-grid">

                                        <article className="metric-card">

                                            <span>
                                                Best Accuracy
                                            </span>

                                            <strong>
                                                100%
                                            </strong>

                                            <small>
                                                ↑ Verified model
                                            </small>

                                        </article>


                                        <article className="metric-card">

                                            <span>
                                                Active Models
                                            </span>

                                            <strong>
                                                03
                                            </strong>

                                            <small>
                                                Registry managed
                                            </small>

                                        </article>


                                        <article className="metric-card">

                                            <span>
                                                Experiments
                                            </span>

                                            <strong>
                                                12
                                            </strong>

                                            <small>
                                                MLflow tracked
                                            </small>

                                        </article>

                                    </div>


                                    <div className="chart-card">

                                        <div className="chart-header">

                                            <div>

                                                <span>
                                                    PERFORMANCE
                                                </span>

                                                <strong>
                                                    Model Evaluation
                                                </strong>

                                            </div>


                                            <small>
                                                Latest run
                                            </small>

                                        </div>


                                        <div className="chart-area">

                                            <div className="chart-bars">

                                                <span />

                                                <span />

                                                <span />

                                                <span />

                                                <span />

                                                <span />

                                                <span />

                                            </div>

                                        </div>

                                    </div>

                                </div>

                            </div>

                        </div>

                    </div>

                </div>

            </section>


            {/* ==================================================
                Statistics
            ================================================== */}

            <section className="statistics-section">

                <div className="container statistics-grid">

                    {platformStats.map((stat) => (

                        <article
                            className="stat-item"
                            key={stat.label}
                        >

                            <strong>
                                {stat.value}
                            </strong>

                            <span>
                                {stat.label}
                            </span>

                        </article>

                    ))}

                </div>

            </section>


            {/* ==================================================
                Features
            ================================================== */}

            <section
                id="features"
                className="features-section"
            >

                <div className="container">

                    <div className="section-heading">

                        <span className="section-label">
                            PLATFORM CAPABILITIES
                        </span>

                        <h2>

                            Everything required to move

                            <span>
                                from data to prediction.
                            </span>

                        </h2>

                        <p>

                            A connected workflow for building,
                            evaluating, tracking, and managing
                            machine-learning models.

                        </p>

                    </div>


                    <div className="feature-grid">

                        {platformFeatures.map(
                            (feature) => (

                                <article
                                    className="feature-card"
                                    key={feature.title}
                                >

                                    <div className="feature-icon">

                                        {feature.icon}

                                    </div>


                                    <h3>

                                        {feature.title}

                                    </h3>


                                    <p>

                                        {feature.description}

                                    </p>


                                    <span className="feature-arrow">

                                        Learn more →

                                    </span>

                                </article>

                            )
                        )}

                    </div>

                </div>

            </section>


            {/* ==================================================
                Workflow
            ================================================== */}

            <section
                id="workflow"
                className="workflow-section"
            >

                <div className="container">

                    <div className="workflow-introduction">

                        <div>

                            <span className="section-label">

                                STRUCTURED WORKFLOW

                            </span>


                            <h2>

                                From raw data to

                                <span>
                                    production prediction.
                                </span>

                            </h2>

                        </div>


                        <p>

                            DataForge organizes the
                            machine-learning lifecycle into
                            clear stages, reducing workflow
                            complexity while keeping
                            experiments and model versions
                            traceable.

                        </p>

                    </div>


                    <div className="workflow-grid">

                        {workflowSteps.map(
                            (step) => (

                                <article
                                    className="workflow-card"
                                    key={step.number}
                                >

                                    <span className="step-number">

                                        {step.number}

                                    </span>


                                    <div className="step-line" />


                                    <h3>

                                        {step.title}

                                    </h3>


                                    <p>

                                        {step.description}

                                    </p>

                                </article>

                            )
                        )}

                    </div>

                </div>

            </section>


            {/* ==================================================
                Final CTA
            ================================================== */}

            <section className="cta-section">

                <div className="container">

                    <div className="cta-card">

                        <div>

                            <span className="section-label">

                                READY TO BUILD

                            </span>


                            <h2>

                                Turn your machine-learning

                                <span>
                                    workflow into a platform.
                                </span>

                            </h2>


                            <p>

                                Start with the DataForge
                                dashboard and explore the
                                complete MLOps workflow.

                            </p>

                        </div>


                        <Link
                            to="/dashboard"
                            className="primary-button"
                        >

                            Open DataForge

                            <span aria-hidden="true">

                                →

                            </span>

                        </Link>

                    </div>

                </div>

            </section>


            {/* ==================================================
                Footer
            ================================================== */}

            <footer className="landing-footer">

                <div className="container footer-content">

                    <div className="footer-brand">

                        <div className="landing-brand">

                            <span className="brand-mark">

                                DF

                            </span>


                            <span className="brand-name">

                                DataForge

                            </span>

                        </div>


                        <p>

                            An end-to-end platform for
                            building and managing
                            machine-learning workflows.

                        </p>

                    </div>


                    <div className="footer-links">

                        <a href="#features">

                            Features

                        </a>

                        <a href="#workflow">

                            Workflow

                        </a>

                        <Link to="/dashboard">

                            Dashboard

                        </Link>

                    </div>

                </div>


                <div className="container footer-bottom">

                    <span>

                        © 2026 DataForge.
                        Built for intelligent workflows.

                    </span>


                    <span>

                        AI • ML • MLOps

                    </span>

                </div>

            </footer>

        </main>
    );
}


export default LandingPage;