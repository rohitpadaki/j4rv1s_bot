# J4RV1S  

J4RV1S is a feature-packed Discord bot designed to enhance server interaction with fun, utility, and AI-driven features.  

## Features  
- **Welcome Message**: Sends a custom welcome message in the `#welcome` channel for new members.  
- **Cat and Dog Pictures**:  
  - Use `/meow` for a random cat picture.  
  - Use `/woof` for a random dog picture.  
- **Yo Momma Jokes**:  
  - Type `yomomma` for a random joke.  
  - Mention someone with `yomomma` to target the joke.
  - Note: Jokes are meant to be taken as they are—just jokes. No offense is intended.
- **Custom User Messages**:  
  - Set personalized responses using `/set` for when someone pings you.  
  - Edit existing messages seamlessly.  
- **Emote Mimic**:  
  - Use `/emote [emote name]` to mimic sending an emote.  
- **AI-Powered Responses**:  
  - Use `/ask` to query Gemini AI for intelligent answers.  
  - Dedicated `#ask-gemini` channel supports conversation history for chat follow-ups.  

## Requirements  
1. Python 3.9 or higher.  
2. Discord API token.  
3. Gemini AI API key.  
4. Libraries:  
   - `discord.py`  
   - `aiohttp`  
   - `google-generativeai`  
   - `json`  

## Installation  

### Clone the Repository  
```bash  
git clone [your-repository-url]  
cd [your-repository-name]  
```  

### Install Dependencies  
```bash  
pip install -r requirements.txt  
```  

### Configuration  
1. **Set Up Environment Variables**:  
   Create a `.env` file in the root directory:  
   ```env  
   BOT_TOKEN=your_discord_token  
   GEMINI_API=your_gemini_api_key  
   ```  

2. **Ensure Permissions**:  
   - Enable `MESSAGE_CONTENT` and `MEMBERS` intents in the Discord Developer Portal for your bot.
   - Enable following permissions: `Read Messages` `Send Messages` `Manage Messages` `Manage Webhooks` `Embed Links` `Attach Files` `Use Slash Commands` `Manage Emojis and Stickers` 

3. **Setup Channel Names**:  
   - Ensure the server has channels named `#welcome`.

### Running the Bot  
```bash  
python main.py  
```  

## Logs  
- All bot activities are logged to a `bot.log` file for easy debugging and monitoring.  
- Error logs are streamlined for readability.  

## Contribution  
Feel free to contribute by submitting issues or creating pull requests.  
