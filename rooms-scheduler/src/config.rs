
use std::sync::Arc;
use lazy_static::lazy_static;

pub struct Config {
    pub port: &'static str,
    pub jwt_secret: &'static str,
    pub jwt_refresh_secret_key: &'static str,
    pub jwt_algorithm: &'static str,
    pub jwt_expire_minutes: u32,
    pub jwt_refresh_expire_days: u32,
}

lazy_static! {
    static ref CONFIG: Arc<Config> = build_config();
}

fn build_config() -> Arc<Config> {
    let port = std::env::var("PORT").unwrap_or_else(|_| "3000".to_string());
    let jwt_secret = std::env::var("JWT_SECRET").unwrap_or_else(|_| "default_secret".to_string());
    let jwt_refresh_secret_key = std::env::var("JWT_REFRESH_SECRET_KEY").unwrap_or_else(|_| "default_refresh_secret".to_string());
    let jwt_algorithm = std::env::var("JWT_ALGORITHM").unwrap_or_else(|_| "HS256".to_string());
    let jwt_expire_minutes = std::env::var("JWT_EXPIRE_MINUTES").unwrap_or_else(|_| "60".to_string()).parse().unwrap_or(60);
    let jwt_refresh_expire_days = std::env::var("JWT_REFRESH_EXPIRE_DAYS").unwrap_or_else(|_| "7".to_string()).parse().unwrap_or(7);

    Arc::new(Config {
        port: Box::leak(port.into_boxed_str()),
        jwt_secret: Box::leak(jwt_secret.into_boxed_str()),
        jwt_refresh_secret_key: Box::leak(jwt_refresh_secret_key.into_boxed_str()),
        jwt_algorithm: Box::leak(jwt_algorithm.into_boxed_str()),
        jwt_expire_minutes,
        jwt_refresh_expire_days,
    })
}

pub fn load_env() -> Arc<Config> {
    CONFIG.clone()
}
