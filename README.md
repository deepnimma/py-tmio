<div align=center>
<h1>py-trackmania.io</h1>

[![Trackmania.io API Status](https://img.shields.io/website?down_message=Offline&label=Trackmania.io%20API&up_message=Online&url=https%3A%2F%2Ftrackmania.io)](https://trackmania.io)

[![GitHub issues](https://img.shields.io/github/issues/NottCurious/py-tmio?logo=github)](https://github.com/NottCurious/py-tmio/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/NottCurious/py-tmio?logo=github)](https://github.com/NottCurious/py-tmio/pulls)
[![GitHub Repo stars](https://img.shields.io/github/stars/NottCurious/py-tmio?logo=github&style=flat-square)](https://github.com/NottCurious/py-tmio/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/NottCurious/py-tmio?style=flat-square)](https://github.com/NottCurious/py-tmio/network/members)

An Asyncio Friendly Trackmania API Wrapper for Python!
</div>

## Important - [Trackmania.io API for my own project?](https://openplanet.dev/tmio/api)

*See below on how to set your user agent*

Your User-Agent Must Have:

1. Your Discord Username
2. Your Project Name

Example:
`NottCurious#4351 | TMIndiaBot`

*" | via py-tmio" is automatically appended to your user agent*

#### How to set user agent.

```python
from trackmania import Client

Client.USER_AGENT = "NottCurious#4351 | TMIndiaBot"
```

#### How to set Redis Server Settings

```python
from trackmania import Client

Client.REDIS_HOST = "127.0.0.1" # 127.0.0.1 is default
Client.REDIS_PORT = 6379 # 6379 is default
Client.REDIS_DB = 0 # 0 is default
Client.REDIS_PASSWORD = "yadayadayada" # Defaults to None. Don't need to change this if your redis server does not have a password.
```

## Docs

Docs can be found on [readthedocs.org](https://py-trackmaniaio.readthedocs.io/en/latest/).

## Installation

**Note:** Must have Python 3.10 or higher.

```shell
python3 -m pip install py-tmio # Linux

python -m pip install py-tmio # Windows
```

## Caching

Caching is done using a redis server. The client defaults to `127.0.0.1:6379`.

Caching is not *required* but is highly recommended.

## April Roadmap
#### By April 8th
3. Implement TMMap Class (or rename COTD Map class)
	* Parameters
		1. environment
		2. exchange
		3. exchange_id
		4. file_name
		5. id
		6. leaderboard
		7. medal_times
		8. name
		9. storage_id
		10. thumbnail
		11. thumbnail_cached
		12. uid
		13. uploaded
		14. url
	* Functions
		1. author
		2. leaderboard_get(position)
		3. submitter()

4. Implement Room Class
	* Parameters
		1. id
		2. image_url
		3. is_cloud
		4. login
		5. max_players_count
		6. name
		7. player_count
		8. region
		9. script
		10. script_settings
	* Functions
		1. club()
		2. maps()

5. Implement ClubActivity class
	* Parameters
		1. external_id
		2. id
		3. is_password_protected
		4. is_public
		5. media
		6. name
		7. type
	* Functions
		1. campaign()
		2. room()

6. Implement ClubMember class
	* Parameters
		1. is_admin
		2. is_creator
		3. is_vip
		4. join_date
		5. role

	* Functions
		1. member()

7. Implement Club Class
	* Parameters
		1. background
		2. created_at
		3. decal
		4. description
		5. featured
		6. id
		7. logo
		8. member_count
		9. name
		10. popularity
		11. screens
		12. state
		13. tag
		14. vertical
	* Functions
		1. creator()
		2. fetch_activities(page)
		3. fetch_members(page)

8. Implement Campaign class
	* Parameters
		1. created_at
		2. id
		3. image
		4. is_official
		5. leaderboard_id
		6. map_count
		7. media
		8. name
		9. uploaded_at
	* Functions
		1. club()
		2. leaderboard()
		3. map(index)
		4. maps()

9. Implement CampaignSearchResult class
	* Parameters
		1. club_id
		2. date
		3. id
		4. map_count
		5. name
	* Functions
		1. get_campaign()

10. Implement CampaignMedia class
	* Parameters
		1. button_background
		2. button_foreground
		3. decal
		4. live_button_background
		5. live_button_foreground
		6. popup
		7. popup_background


11. Implement CampaignLeaderboard class
	* Parameters
		1.
	* Functions

8. Implement the Campaign Manager class
	* Functions
		1. current_season
		2. get(club_id, id)
		3. official_campaigns()
		4. popular_campaigns(page)
		5. search(query, page)



#### By April 15th
1. Implement MapManager class
	* Functions
		1. get()

## Examples

### Latest TOTD

```python
from trackmania.managers import totd_manager

# In Async Function
latest_totd = await totd_manager.latest_totd()

print(latest_totd.map_name)
```

## Pull Requests and Issues

If you have any suggestions, bugs, fixes or enhancements, please open
a [Pull Request](https://github.com/NottCurious/py-tmio/compare)
or [Issue](https://github.com/NottCurious/py-tmio/issues/new)

## Discord

Contact me on Discord if you have any questions, NottCurious#4351

## License

[MIT License](https://mit-license.org/)
