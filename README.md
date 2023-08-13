# FeeDon This!
FeeDon This! is a service for Mastodon instances that allows users to generate RSS feeds from their home timeline, local timeline, and any lists they've created. Technically speaking you can _mostly_ do this by just subscribing to individual users' timelines in your RSS reader, but this doesn't work well if you want to keep your RSS reader in-sync with who you follow or follow users with private posts.

<img src="https://git.sr.ht/~vesto/feedon-this/blob/1cd87db7167f9d19fce10d52f37a62d20a05c8fe/docs/images/screenshot.png" width="400" alt="A screenshot of FeedOn in action" />

## Getting started
While it's perfectly possible to run your own instance, it's much easier to use somebody else's instance. If this takes off I hope to run a publicly accessible instance for others, but given that the project is still in its early phases I'm limiting my instance for a select number of testers.

If you'd like to help me test things out and provide feedback, feel free to [send an email](mailto:steve@stevegattuso.me) and I'll consider adding you in.

## Setup
Setting up a development instance is a bit tricky, as you really need to expose your instance to the internet at large in order for it to work properly. There are a variety of ways to accomplish this, and for the sake of brevity I'm going to avoid getting too far into the weeds on this for the time being. My personal dev setup involves running the Flask server on a VPS that uses [Caddy](https://caddyserver.com/) as a reverse proxy (with SSL).

To set up the project itself, run the following commands to clone the repo and install dependencies:

```
git clone https://git.sr.ht/~vesto/feedon-this
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

Once dependencies have been installed you'll need to create a `.env` file to configure your server:

```
SECRET_KEY=[long random string]
BASE_URL=https://your.instance.domain.com
```

Finally, you can spin up your server by running the following command:

```
flask --app feedon run -h 0.0.0.0 --debug -p 8000
```

If all goes well you should have a development server up and running and can navigate to your `BASE_URL` to log in and create some RSS feeds.

## Contributing
You've probably already noticed that this project is a bit different than other open source projects you've interacted with. We're on SourceHut instead of GitHub! Not to fear though- if you're interested in reporting a bug you can use the [issue tracker](https://todo.sr.ht/~vesto/feedon-this) or for general discussion you can send an email to the [mailing list](https://lists.sr.ht/~vesto/feedon-this).

I'm pretty new to using SourceHut, so let's see how this goes!

## License
This project is licensed under the GNU General Public License v3. More information can be found in the LICENSE.txt file.
