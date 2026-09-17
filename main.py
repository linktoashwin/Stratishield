import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Scope allows read-only access to Google Calendar
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


# Converts Google's event format into a standard format
def format_calendar_event(event):

    start = event["start"].get(
        "dateTime",
        event["start"].get("date")
    )

    end = event["end"].get(
        "dateTime",
        event["end"].get("date")
    )

    return {
        "eventId": event.get("id"),
        "summary": event.get(
            "summary",
            "No title"
        ),
        "start": start,
        "end": end,
        "description": event.get(
            "description",
            "No description"
        ),
        "location": event.get(
            "location",
            "No location"
        )
    }


# Gets the next 10 upcoming calendar events
def get_calendar_events(service):

    now = datetime.datetime.now(
        tz=datetime.timezone.utc
    ).isoformat()

    print("Getting the upcoming 10 events")

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = events_result.get("items", [])

    if not events:
        print("No upcoming events found.")
        return []

    calendar_events = []

    for event in events:

        calendar_event = format_calendar_event(
            event
        )

        print(
            calendar_event["start"],
            calendar_event["summary"]
        )

        calendar_events.append(
            calendar_event
        )

    return calendar_events


# Gets one specific event using its Google event ID
def get_calendar_event(service, event_id):

    event = (
        service.events()
        .get(
            calendarId="primary",
            eventId=event_id
        )
        .execute()
    )

    return format_calendar_event(event)


# Gets all events for a specific date
def get_events_by_date(service, date):

    # Uses the computer's local timezone
    local_timezone = (
        datetime.datetime.now()
        .astimezone()
        .tzinfo
    )

    # Beginning of the selected day
    start_of_day = datetime.datetime.combine(
        date,
        datetime.time.min,
        tzinfo=local_timezone
    )

    # Beginning of the following day
    end_of_day = (
        start_of_day
        + datetime.timedelta(days=1)
    )

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_of_day.isoformat(),
            timeMax=end_of_day.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = events_result.get("items", [])

    calendar_events = []

    for event in events:

        calendar_events.append(
            format_calendar_event(event)
        )

    return calendar_events


def main():

    creds = None

    # Check if the user has already logged in before
    if os.path.exists("token.json"):

        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )


    # If credentials are missing or invalid
    if not creds or not creds.valid:

        # Refresh expired credentials
        if (
            creds
            and creds.expired
            and creds.refresh_token
        ):

            creds.refresh(Request())

        # Otherwise, have the user log in
        else:

            flow = (
                InstalledAppFlow
                .from_client_secrets_file(
                    "credentials.json",
                    SCOPES
                )
            )

            creds = flow.run_local_server(
                port=0
            )


        # Save login information for next time
        with open(
            "token.json",
            "w"
        ) as token:

            token.write(
                creds.to_json()
            )


    try:

        # Connect to Google Calendar API
        service = build(
            "calendar",
            "v3",
            credentials=creds
        )


        # Get upcoming calendar events
        calendar_events = (
            get_calendar_events(service)
        )


        return calendar_events


    except HttpError as error:

        print(
            f"An error occurred: {error}"
        )

        return []


if __name__ == "__main__":

    main()
