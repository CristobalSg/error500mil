FROM rust:1.91-alpine3.22 AS builder

WORKDIR /app

COPY Cargo.toml Cargo.lock ./

RUN mkdir src

COPY src ./src

RUN apk add --no-cache \
    build-base \
    musl-dev

RUN cargo build --release

FROM alpine:3.22

COPY --from=builder /app/target/release/rooms-scheduler /usr/bin/rooms-scheduler

RUN rm -rf /var/cache/apk/* && rm -rf /app

CMD ["/usr/bin/rooms-scheduler"]