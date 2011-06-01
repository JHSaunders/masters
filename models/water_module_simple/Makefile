all: res.json

#res.json: obs.json cpts.json
#	./social_ecological cpts.json obs.json > res.json

res.json: obs.json cpts.json
	jdbn inference -m cpts.json -p obs.json -o res.json

obs.json: prm.json model.json
	jdbn obs -m model.json -p prm.json -o obs.json

cpts.json: model.json
	jdbn cpts -i model.json -o cpts.json -s 10

clean:
	rm -f obs.json res.json cpts.json simple.json

