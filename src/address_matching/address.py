class Address:
    def __init__(self, city, district, neighbourhood, label):
        self.city = city
        self.district = district
        self.neighbourhood = neighbourhood
        self.label = label



    def get_label(self):
        return self.label

    def get_neighbourhood(self):
        return self.neighbourhood

    def get_city(self):
        return self.city

    def get_district(self):
        return self.district
