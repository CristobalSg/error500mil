mod config;
mod router;
mod controllers;
mod models;
mod middlewares;
mod scheduler;
mod jwt;

use crate::router::create_router;

#[tokio::main]
async fn main() {

    let config = config::load_env();

    let address = format!("0.0.0.0:{}", config.port);
    let listener = tokio::net::TcpListener::bind(address).await.unwrap();

    let app = create_router();

    println!("Iniciando servicio asignador de salas en: 0.0.0.0:{} ...", config.port);
    axum::serve(listener, app).await.unwrap();
}