use axum::{
    middleware::from_fn,
    routing::post,
    Router,
};

use crate::controllers::rooms_scheduler::rooms_scheduler_controller;
use crate::middlewares::{require_access_token, require_administrator_role};

pub fn create_router() -> Router {
    Router::new()
        .route("/api/v1/rooms/schedule", post(rooms_scheduler_controller)
            .route_layer(from_fn(require_access_token))
            .route_layer(from_fn(require_administrator_role))
        )
}
