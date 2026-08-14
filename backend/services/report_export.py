import os
import zipfile
import json

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from backend.config.paths import REPORT_DIR, MODELS_DIR
from backend.utils.logger import logger


class Exporter:

    def __init__(
        self,
        reports_dir: str = str(REPORT_DIR),
        models_dir: str = str(MODELS_DIR),
    ):
        self.reports_dir = reports_dir
        self.models_dir = models_dir

    # ==================================================
    # Generate PDF Report
    # ==================================================

    def _generate_pdf_report(
        self,
        df_clean,
        activity_log,
        metrics,
    ):
        pdf_path = os.path.join(
            self.reports_dir,
            "report.pdf",
        )

        styles = getSampleStyleSheet()
        story = []

        # ------------------------------------------------
        # Title
        # ------------------------------------------------

        story.append(
            Paragraph(
                "<b>DataForge Report</b>",
                styles["Title"],
            )
        )

        story.append(Spacer(1, 20))

        # ------------------------------------------------
        # Dataset Information
        # ------------------------------------------------

        story.append(
            Paragraph(
                "<b>Dataset Information</b>",
                styles["Heading2"],
            )
        )

        story.append(
            Paragraph(
                f"Rows: {df_clean.shape[0]}, "
                f"Columns: {df_clean.shape[1]}",
                styles["Normal"],
            )
        )

        story.append(Spacer(1, 12))

        # ------------------------------------------------
        # Cleaning Steps
        # ------------------------------------------------

        if "cleaning_steps" in activity_log:

            story.append(
                Paragraph(
                    "<b>Cleaning Steps</b>",
                    styles["Heading2"],
                )
            )

            for step in activity_log["cleaning_steps"]:

                story.append(
                    Paragraph(
                        f"• {step}",
                        styles["Normal"],
                    )
                )

            story.append(Spacer(1, 12))

        # ------------------------------------------------
        # Visualizations
        # ------------------------------------------------

        if "visualizations" in activity_log:

            story.append(
                Paragraph(
                    "<b>Visualizations</b>",
                    styles["Heading2"],
                )
            )

            for viz in activity_log["visualizations"]:

                if isinstance(viz, dict):

                    story.append(
                        Paragraph(
                            f"• {viz.get('name', 'Visualization')}",
                            styles["Normal"],
                        )
                    )

                    viz_path = viz.get("path")

                    if viz_path and os.path.exists(viz_path):

                        story.append(
                            Image(
                                viz_path,
                                width=400,
                                height=250,
                            )
                        )

                else:

                    story.append(
                        Paragraph(
                            f"• {viz}",
                            styles["Normal"],
                        )
                    )

            story.append(Spacer(1, 12))

        # ------------------------------------------------
        # Model Training
        # ------------------------------------------------

        if "model_training" in activity_log:

            story.append(
                Paragraph(
                    "<b>Model Training</b>",
                    styles["Heading2"],
                )
            )

            model_trainings = activity_log["model_training"]

            if isinstance(model_trainings, dict):
                model_trainings = [model_trainings]

            elif isinstance(model_trainings, str):
                model_trainings = [model_trainings]

            for training in model_trainings:

                if isinstance(training, dict):

                    story.append(
                        Paragraph(
                            f"Target Column: "
                            f"{training.get('target', 'N/A')}",
                            styles["Normal"],
                        )
                    )

                    story.append(
                        Paragraph(
                            f"Chosen Model: "
                            f"{training.get('chosen_model', 'N/A')}",
                            styles["Normal"],
                        )
                    )

                    story.append(
                        Paragraph(
                            f"Train Split: "
                            f"{training.get('train_split', 'N/A')}, "
                            f"Test Split: "
                            f"{training.get('test_split', 'N/A')}",
                            styles["Normal"],
                        )
                    )

                    story.append(Spacer(1, 6))

                    if "metrics" in training:

                        data = [
                            ["Metric", "Value"]
                        ] + [
                            [key, str(value)]
                            for key, value
                            in training["metrics"].items()
                        ]

                        table = Table(
                            data,
                            hAlign="LEFT",
                        )

                        table.setStyle(
                            TableStyle(
                                [
                                    (
                                        "BACKGROUND",
                                        (0, 0),
                                        (-1, 0),
                                        colors.grey,
                                    ),
                                    (
                                        "TEXTCOLOR",
                                        (0, 0),
                                        (-1, 0),
                                        colors.whitesmoke,
                                    ),
                                    (
                                        "ALIGN",
                                        (0, 0),
                                        (-1, -1),
                                        "CENTER",
                                    ),
                                    (
                                        "FONTNAME",
                                        (0, 0),
                                        (-1, 0),
                                        "Helvetica-Bold",
                                    ),
                                    (
                                        "BOTTOMPADDING",
                                        (0, 0),
                                        (-1, 0),
                                        12,
                                    ),
                                    (
                                        "BACKGROUND",
                                        (0, 1),
                                        (-1, -1),
                                        colors.beige,
                                    ),
                                ]
                            )
                        )

                        story.append(table)
                        story.append(Spacer(1, 12))

                else:

                    story.append(
                        Paragraph(
                            f"• {training}",
                            styles["Normal"],
                        )
                    )

                    story.append(Spacer(1, 6))

        # ------------------------------------------------
        # Footer
        # ------------------------------------------------

        story.append(Spacer(1, 40))

        story.append(
            Paragraph(
                "DataForge by Mysterious | Hassan",
                styles["Normal"],
            )
        )

        # ------------------------------------------------
        # Build PDF
        # ------------------------------------------------

        logger.info("Generating PDF report...")

        os.makedirs(
            self.reports_dir,
            exist_ok=True,
        )

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
        )

        doc.build(story)

        logger.info(
            f"PDF report generated: {pdf_path}"
        )

        return pdf_path

    # ==================================================
    # Create Full Report
    # ==================================================

    def create_full_report(
        self,
        df_clean,
        activity_log,
        metrics,
    ):
        os.makedirs(
            self.reports_dir,
            exist_ok=True,
        )

        logger.info(
            "Creating full DataForge report..."
        )

        # ------------------------------------------------
        # Cleaned Dataset
        # ------------------------------------------------

        clean_path = os.path.join(
            self.reports_dir,
            "cleaned_dataset.csv",
        )

        df_clean.to_csv(
            clean_path,
            index=False,
        )

        logger.info(
            f"Cleaned dataset saved: {clean_path}"
        )

        # ------------------------------------------------
        # Activity Log
        # ------------------------------------------------

        json_path = os.path.join(
            self.reports_dir,
            "activity_log.json",
        )

        with open(
            json_path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                activity_log,
                f,
                indent=4,
                ensure_ascii=False,
            )

        logger.info(
            f"Activity log saved: {json_path}"
        )

        # ------------------------------------------------
        # PDF
        # ------------------------------------------------

        pdf_path = self._generate_pdf_report(
            df_clean,
            activity_log,
            metrics,
        )

        # ------------------------------------------------
        # ZIP Package
        # ------------------------------------------------

        zip_path = os.path.join(
            self.reports_dir,
            "dataforge_report.zip",
        )

        logger.info(
            "Creating ZIP package..."
        )

        with zipfile.ZipFile(
            zip_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
        ) as zipf:

            # Report files
            zipf.write(
                clean_path,
                arcname="cleaned_dataset.csv",
            )

            zipf.write(
                json_path,
                arcname="activity_log.json",
            )

            zipf.write(
                pdf_path,
                arcname="report.pdf",
            )

            # ------------------------------------------------
            # Recursive Model Packaging
            # ------------------------------------------------

            if os.path.isdir(self.models_dir):

                for root, _, files in os.walk(
                    self.models_dir
                ):

                    for filename in files:

                        file_path = os.path.join(
                            root,
                            filename,
                        )

                        if not os.path.isfile(file_path):
                            continue

                        relative_path = os.path.relpath(
                            file_path,
                            self.models_dir,
                        )

                        archive_path = os.path.join(
                            "models",
                            relative_path,
                        ).replace("\\", "/")

                        zipf.write(
                            file_path,
                            arcname=archive_path,
                        )

                        logger.info(
                            f"Added model artifact: "
                            f"{archive_path}"
                        )

        logger.info(
            f"Report exported successfully: {zip_path}"
        )

        return zip_path