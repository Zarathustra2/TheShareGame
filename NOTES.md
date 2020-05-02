#### Auth Github
1. Update Sites from example.com => thesharegame.com (Database migration)
2. Go to admin panel register github, don't forget to add the site
3. Make sure on github.com the uri is set to thesharegame.com


#### env
For docker-compose make sure .env exists. Run
```bash
cp default.env .env
```
Update the values and moreover run:
```bash
> cd frontend
> cp .env.default .env.production.local
```
And again update/set the values!
