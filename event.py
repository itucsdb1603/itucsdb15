class Event:
    def __init__(self, content, event_date, place):
        self.content = content
        self.event_date = event_date
        self.place = place
    
    def update_event(self, new_content, new_place, new_date):
        self.content = new_content
        self.event_date = new_date
        self.place = new_place