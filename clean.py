import asyncio
import aiohttp
import discord 
import time
import hashlib
import os 
import os.path
import sys

async def discord_login(username, password):
	cache_name = f'cache_{hashlib.sha1((username + password).encode("utf8")).hexdigest()}.dat'
	async with aiohttp.ClientSession() as session:
		if os.path.exists(cache_name):
			with open(cache_name, "r", encoding="utf8") as file:
				return file.read()
		response = await session.request(
			"POST",
			"https://discord.com/api/v9/auth/login",
			json={
				"login": username,
				"password": password,
				"undelete": False,
				"captcha_key": None,
				"login_source": None,
				"gift_code_sku_id": None
			}
		)
		response = await response.json()
		with open(cache_name, "w", encoding="utf8") as file:
			file.write(response["token"])
		return response["token"]


client = discord.Client(self_bot=True)

@client.event
async def on_ready():
	print( "Logged in as {} ({})".format( client.user.name, client.user.id ) )
	print( "" )
	print( "="*20 )

	for channel in client.private_channels:
		permissions = channel.permissions_for(client.user)
		if input(f'Nuke {channel} {channel.type} kick:{permissions.kick_members} chat:{permissions.manage_messages}?') == "y":
			if channel.type == "group":
				for member in channel.members:
					if member.user != client.user:
						print(member)
						if permissions.kick_members:
							await member.kick()

			async for message in channel.history(limit=None):
				if not permissions.manage_messages and message.author != client.user: continue
				print("> ", message.content, " "*20, end="\r")
				try:
					await message.delete()
				except Exception as error:
					print(error)


async def main():
	while True:
		try:
			loop = asyncio.new_event_loop()
			asyncio.set_event_loop(loop)
			token = await discord_login(sys.argv[1], sys.argv[2])
			await client.start(token, bot=False)
		except Exception as error:
			raise 
		await asyncio.sleep(1)

if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())