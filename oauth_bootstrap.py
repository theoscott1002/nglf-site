from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def main():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)  # opens browser to authorize
    with open("token.json", "w") as f:
        f.write(creds.to_json())
    print("✅ token.json created")

if __name__ == "__main__":
    main()
