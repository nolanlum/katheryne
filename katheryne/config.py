import os


def get_file_contents(filename):
    with open(filename, 'r') as f:
        return f.read().strip()


TOKEN = get_file_contents(os.environ.get('KATHERYNE_DISCORD_TOKEN_FILE', '.discord_token'))

