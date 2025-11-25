use crate::{models::ActivitiesRequest, scheduler::algorithm::run_scheduler};

use axum::extract::Json;
use axum_responses::{Result, http::HttpResponse};

pub async fn rooms_scheduler_controller(Json(body): Json<ActivitiesRequest>) -> Result<HttpResponse> {
    // Placeholder for rooms scheduler controller logic

    let activities = body.activities;
    let rooms = body.rooms;

    let (scheduled_activities, unscheduled_activities) = run_scheduler(activities, rooms)?;

    Ok(HttpResponse::Ok()
        .message("activities scheduled successfully")
        .data(scheduled_activities)
        .data(unscheduled_activities)
    )
}