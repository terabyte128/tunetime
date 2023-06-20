.PHONY: db
db:
	docker run --name tunetime-db -p 5432:5432 \
		-e POSTGRES_USER=tunetime \
		-e POSTGRES_PASSWORD=tunetime \
		-e POSTGRES_DB=tunetime \
		--detach \
		postgres

.PHONY: stop-db
stop-db:
	docker stop tunetime-db
	docker container rm tunetime-db
