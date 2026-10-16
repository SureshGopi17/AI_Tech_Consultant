"""
Agent 3: Technical Estimator / Lead Developer Agent.
Breaks custom development requirements into modular technical tasks,
assigns realistic engineering hour estimates, QA buffers, and calculates costs.
"""

from typing import List, Tuple
from app.models import RequirementItem, DeveloperTask, TaskBreakdown

class TechnicalEstimatorAgent:
    def __init__(self, hourly_rate: float = 95.0):
        self.role = "Lead Technical Estimator"
        self.hourly_rate = hourly_rate

    def create_estimate(self, requirements: List[RequirementItem]) -> TaskBreakdown:
        """
        Translates evaluated requirements into structured developer tasks with hour estimates.
        """
        tasks: List[DeveloperTask] = []
        task_counter = 1

        for req in requirements:
            if req.is_native_setting:
                # Native setting takes 0 custom development hours
                tasks.append(DeveloperTask(
                    id=f"TSK-{task_counter:03d}",
                    requirement_id=req.id,
                    task_name=f"Configure Native Setting: {req.title}",
                    description=f"Admin configuration under {req.native_setting_path}. Zero custom code required.",
                    dev_type="Configuration",
                    estimated_hours=1.0,
                    hourly_rate=self.hourly_rate,
                    cost=1.0 * self.hourly_rate
                ))
            else:
                # Custom engineering breakdown
                title_lower = req.title.lower()
                if "bar" in title_lower or "verification" in title_lower:
                    tasks.append(DeveloperTask(
                        id=f"TSK-{task_counter:03d}",
                        requirement_id=req.id,
                        task_name="Custom Form Field & State Bar Verification Hook",
                        description="Inject custom Bar Number field into Member Form, build webhook receiver, and conditional 'Bar Verified' badge widget.",
                        dev_type="API/Webhook",
                        estimated_hours=10.0,
                        hourly_rate=self.hourly_rate,
                        cost=10.0 * self.hourly_rate
                    ))
                elif "theme" in title_lower or "branding" in title_lower or "design" in title_lower:
                    tasks.append(DeveloperTask(
                        id=f"TSK-{task_counter:03d}",
                        requirement_id=req.id,
                        task_name="Custom CSS Theme, Google Fonts & Homepage Layout",
                        description="Implement Navy & Gold brand palette, typography pairings, hero banner layout, and mobile-responsive overrides.",
                        dev_type="Frontend",
                        estimated_hours=14.0,
                        hourly_rate=self.hourly_rate,
                        cost=14.0 * self.hourly_rate
                    ))
                elif "csv" in title_lower or "import" in title_lower or "migration" in title_lower:
                    tasks.append(DeveloperTask(
                        id=f"TSK-{task_counter:03d}",
                        requirement_id=req.id,
                        task_name="CSV Data Cleaning, Field Mapping & Geocode Ingestion",
                        description="Normalize Excel dataset, verify address geocoding coordinates, and execute batch CSV import.",
                        dev_type="Configuration",
                        estimated_hours=6.0,
                        hourly_rate=self.hourly_rate,
                        cost=6.0 * self.hourly_rate
                    ))
                else:
                    tasks.append(DeveloperTask(
                        id=f"TSK-{task_counter:03d}",
                        requirement_id=req.id,
                        task_name=f"Custom Dev: {req.title}",
                        description=req.notes or "Custom template widget and backend integration.",
                        dev_type="Frontend",
                        estimated_hours=8.0,
                        hourly_rate=self.hourly_rate,
                        cost=8.0 * self.hourly_rate
                    ))
            task_counter += 1

        dev_hours = sum(t.estimated_hours for t in tasks)
        qa_buffer = round(dev_hours * 0.15, 1)  # 15% QA buffer
        pm_hours = round(dev_hours * 0.10, 1)   # 10% Project Management & client walkthrough

        total_hours = round(dev_hours + qa_buffer + pm_hours, 1)
        total_cost = round(total_hours * self.hourly_rate, 2)

        return TaskBreakdown(
            tasks=tasks,
            total_hours=total_hours,
            total_cost=total_cost,
            qa_buffer_hours=qa_buffer,
            project_management_hours=pm_hours
        )

estimator_agent = TechnicalEstimatorAgent()
