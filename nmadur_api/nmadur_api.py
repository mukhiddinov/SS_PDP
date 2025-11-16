# nmadur_api.py
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# Default Google Sheet parametrlari
CREDS_FILE = "service_account.json"
DAY_BLOCK_SIZE = 7
DAY_NAMES = {
    "Monday": "Dushanba",
    "Tuesday": "Seshanba",
    "Wednesday": "Chorshanba",
    "Thursday": "Payshanba",
    "Friday": "Juma",
    "Saturday": "Shanba",
    "Sunday": "Yakshanba"
}
PARA_TIMES = [
    "09:00 - 10:20",
    "10:30 - 11:50",
    "12:00 - 13:20",
    "14:20 - 15:40",
    "15:50 - 17:10",
    "17:20 - 18:40",
    "18:50 - 20:10"
]

app = FastAPI(title="Class Schedule API")

class ScheduleRequest(BaseModel):
    spreadsheet_id: str
    sheet_name: str
    class_name: str
    day_name: str

# Funksiyalar (logikani o'zgartirmadik)
def find_day_column_indexes(first_row):
    day_positions = {}
    for i, cell in enumerate(first_row):
        if not cell:
            continue
        for eng, uz in DAY_NAMES.items():
            if eng in cell or uz in cell:
                day_positions[eng] = i
                break
    return day_positions

def extract_full_day_schedule(all_rows, start_col):
    schedule_blocks = []
    i = 0
    while i < len(all_rows):
        class_name = all_rows[i][0] if all_rows[i] else ""
        lessons = []
        block_rows = all_rows[i:i+4]
        if not any(block_rows):
            i += 4
            continue
        for para_index in range(DAY_BLOCK_SIZE):
            subject = block_rows[0][start_col + para_index] if para_index < len(block_rows[0]) - start_col else ""
            teacher = block_rows[1][start_col + para_index] if para_index < len(block_rows[1]) - start_col else ""
            groups = block_rows[2][start_col + para_index] if para_index < len(block_rows[2]) - start_col else ""
            room = block_rows[3][start_col + para_index] if para_index < len(block_rows[3]) - start_col else ""
            if any([subject, teacher, groups, room]):
                lessons.append({
                    "para": para_index + 1,
                    "time": PARA_TIMES[para_index],
                    "subject": subject,
                    "teacher": teacher,
                    "groups": groups,
                    "room": room
                })
        schedule_blocks.append({
            "class": class_name,
            "lessons": lessons
        })
        i += 4
    return schedule_blocks

def get_class_schedule(class_name, day_name, rows, day_positions):
    if day_name not in day_positions:
        return []
    start_col = day_positions[day_name]
    day_schedule = extract_full_day_schedule(rows[2:], start_col)
    result = []
    for i in range(0, len(day_schedule), 1):
        block = day_schedule[i]
        if block["class"] == class_name or (i > 0 and not block["class"]):
            result.extend(block["lessons"])
    return result

@app.post("/schedule/")
def fetch_schedule(req: ScheduleRequest):
    try:
        creds = Credentials.from_service_account_file(
            CREDS_FILE,
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
        service = build("sheets", "v4", credentials=creds)
        RANGE = f"{req.sheet_name}!A1:ZZ200"
        sheet = service.spreadsheets().values().get(
            spreadsheetId=req.spreadsheet_id,
            range=RANGE
        ).execute()
        rows = sheet.get("values", [])
        if not rows:
            raise HTTPException(status_code=404, detail="Jadval bo'sh")
        day_positions = find_day_column_indexes(rows[0])
        schedule = get_class_schedule(req.class_name, req.day_name, rows, day_positions)
        return schedule
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
