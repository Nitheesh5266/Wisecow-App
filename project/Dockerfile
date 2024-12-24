FROM golang:1.19-alpine AS builder

WORKDIR /app
COPY . .
RUN go build -o wisecow

FROM alpine:3.17

WORKDIR /app
COPY --from=builder /app/wisecow /app/wisecow
COPY --from=builder /app/data /app/data

EXPOSE 8080
CMD ["/app/wisecow"]