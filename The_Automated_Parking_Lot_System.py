"""Automated Parking Lot System with GUI interface."""
import tkinter as tk
from tkinter import ttk, messagebox
import time
from datetime import datetime
import random
from enum import Enum

# Custom Exception for Parking Lot
class ParkingLotFullError(Exception):
    """Custom exception for when parking lot is full"""
    def __init__(self, message="Parking lot is full!"):
        super().__init__(message)

class VehicleType(Enum):
    """Enum for vehicle types"""
    CAR = "Car"
    BIKE = "Bike"
    TRUCK = "Truck"
    SUV = "SUV"

class Vehicle:
    """Base Vehicle class"""
    def __init__(self, vehicle_id, vehicle_type, owner_name="Unknown"):
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type
        self.owner_name = owner_name
        self.entry_time = None
        self.slot_number = None
        self.color = self.generate_color()

    def generate_color(self):
        """Generate a color based on vehicle type"""
        colors = {
            VehicleType.CAR: ["#3498db", "#2980b9", "#1abc9c"],
            VehicleType.BIKE: ["#e74c3c", "#c0392b", "#d35400"],
            VehicleType.TRUCK: ["#f39c12", "#e67e22", "#d68910"],
            VehicleType.SUV: ["#9b59b6", "#8e44ad", "#7d3c98"]
        }
        return random.choice(colors.get(self.vehicle_type, ["#95a5a6"]))

    def get_parking_fee(self, exit_time):
        """Calculate parking fee based on hours parked"""
        if not self.entry_time:
            return 0

        hours_parked = (exit_time - self.entry_time).total_seconds() / 3600
        hours_parked = max(1, hours_parked)
        hours_parked = (hours_parked + 0.99) // 1

        rates = {
            VehicleType.CAR: 2.0,
            VehicleType.BIKE: 1.0,
            VehicleType.TRUCK: 3.0,
            VehicleType.SUV: 2.5
        }

        rate = rates.get(self.vehicle_type, 2.0)
        return hours_parked * rate

    def to_dict(self):
        """Convert vehicle object to dictionary"""
        return {
            "id": self.vehicle_id,
            "type": self.vehicle_type.value,
            "owner": self.owner_name,
            "entry_time": (self.entry_time.strftime("%H:%M:%S")
                           if self.entry_time else "N/A"),
            "slot": self.slot_number,
            "color": self.color
        }

class Car(Vehicle):
    """Car vehicle type"""
    def __init__(self, vehicle_id, owner_name="Unknown"):
        super().__init__(vehicle_id, VehicleType.CAR, owner_name)

class Bike(Vehicle):
    """Bike vehicle type"""
    def __init__(self, vehicle_id, owner_name="Unknown"):
        super().__init__(vehicle_id, VehicleType.BIKE, owner_name)

class Truck(Vehicle):
    """Truck vehicle type"""
    def __init__(self, vehicle_id, owner_name="Unknown"):
        super().__init__(vehicle_id, VehicleType.TRUCK, owner_name)

class SUV(Vehicle):
    """SUV vehicle type"""
    def __init__(self, vehicle_id, owner_name="Unknown"):
        super().__init__(vehicle_id, VehicleType.SUV, owner_name)

class ParkingLot:
    """Parking Lot class with limited capacity"""
    def __init__(self, capacity=5):
        self.capacity = capacity
        self.slots = [None] * capacity
        self.vehicles = {}
        self.hourly_rate = 2.0
        self.revenue = 0.0
        self.total_vehicles = 0

    def park_vehicle(self, vehicle):
        """Park a vehicle in the nearest empty slot"""
        if self.is_full():
            raise ParkingLotFullError()

        for slot_number in range(self.capacity):
            if self.slots[slot_number] is None:
                vehicle.slot_number = slot_number + 1
                vehicle.entry_time = datetime.now()
                self.slots[slot_number] = vehicle
                self.vehicles[vehicle.vehicle_id] = vehicle
                self.total_vehicles += 1
                return slot_number + 1

        raise ParkingLotFullError()

    def remove_vehicle(self, vehicle_id):
        """Remove a vehicle and calculate parking fee"""
        if vehicle_id not in self.vehicles:
            raise ValueError(f"Vehicle with ID {vehicle_id} not found")

        vehicle = self.vehicles[vehicle_id]
        exit_time = datetime.now()

        fee = vehicle.get_parking_fee(exit_time)
        self.revenue += fee

        if vehicle.slot_number:
            self.slots[vehicle.slot_number - 1] = None

        del self.vehicles[vehicle_id]

        return vehicle, fee

    def is_full(self):
        """Check if parking lot is full"""
        return all(slot is not None for slot in self.slots)

    def is_empty(self):
        """Check if parking lot is empty"""
        return all(slot is None for slot in self.slots)

    def get_available_slots(self):
        """Get list of available slot numbers"""
        return [i + 1 for i, slot in enumerate(self.slots) if slot is None]

    def get_occupied_slots(self):
        """Get list of occupied slot numbers"""
        return [i + 1 for i, slot in enumerate(self.slots) if slot is not None]

    def get_occupancy_rate(self):
        """Get current occupancy rate as percentage"""
        occupied = len(self.get_occupied_slots())
        return (occupied / self.capacity) * 100

    def get_slot_status(self, slot_number):
        """Get status of a specific slot"""
        if 1 <= slot_number <= self.capacity:
            return self.slots[slot_number - 1]
        return None

    def get_total_vehicles_parked(self):
        """Get total number of vehicles currently parked"""
        return len(self.vehicles)

    def reset(self):
        """Reset the parking lot"""
        self.slots = [None] * self.capacity
        self.vehicles.clear()

class AutomatedParkingLotSystem:
    """GUI-based Automated Parking Lot System"""
    def __init__(self, root):
        self.root = root
        self.root.title("Automated Parking Lot System")
        self.root.state('zoomed')
        self.root.configure(bg="#ecf0f1")

        self.parking_lot = ParkingLot(capacity=12)

        self.setup_styles()

        self.create_gui()

        self.initialize_demo_vehicles()

        self.update_real_time_info()

    def setup_styles(self):
        """Setup color schemes and fonts"""
        self.colors = {
            "primary": "#3498db",
            "secondary": "#2c3e50",
            "success": "#2ecc71",
            "danger": "#e74c3c",
            "warning": "#f39c12",
            "info": "#1abc9c",
            "light": "#ecf0f1",
            "dark": "#2c3e50",
            "empty_slot": "#bdc3c7",
            "slot_border": "#7f8c8d"
        }

        self.fonts = {
            "title": ("Segoe UI", 28, "bold"),
            "subtitle": ("Segoe UI", 18, "bold"),
            "normal": ("Segoe UI", 12),
            "small": ("Segoe UI", 10),
            "mono": ("Courier New", 10)
        }

    def create_gui(self):
        """Create the main GUI layout"""
        main_container = tk.Frame(self.root, bg=self.colors["light"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.create_header(main_container)

        content_frame = tk.Frame(main_container, bg=self.colors["light"])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        left_frame = tk.Frame(content_frame, bg=self.colors["light"])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                        padx=(0, 15))

        right_frame = tk.Frame(content_frame, bg=self.colors["light"])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True,
                         padx=(15, 0))

        self.create_parking_lot_visualization(left_frame)
        self.create_vehicle_controls(right_frame)
        self.create_parking_stats(right_frame)
        self.create_vehicle_list(right_frame)

    def create_header(self, parent):
        """Create application header"""
        header_frame = tk.Frame(parent, bg=self.colors["primary"])
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_frame = tk.Frame(header_frame, bg=self.colors["primary"])
        title_frame.pack(fill=tk.X, padx=30, pady=15)

        title_label = tk.Label(
            title_frame,
            text="Automated Parking Lot System",
            font=self.fonts["title"],
            bg=self.colors["primary"],
            fg="white"
        )
        title_label.pack(side=tk.LEFT)

        self.info_bar = tk.Frame(header_frame, bg="#2980b9")
        self.info_bar.pack(fill=tk.X, padx=20, pady=(0, 10))

        self.time_label = tk.Label(
            self.info_bar,
            text="",
            font=self.fonts["small"],
            bg="#2980b9",
            fg="white"
        )
        self.time_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.status_label = tk.Label(
            self.info_bar,
            text="",
            font=self.fonts["small"],
            bg="#2980b9",
            fg="white"
        )
        self.status_label.pack(side=tk.RIGHT, padx=10, pady=5)

    def create_parking_lot_visualization(self, parent):
        """Create visual representation of parking lot"""
        lot_frame = tk.LabelFrame(
            parent,
            text="Parking Lot Layout",
            font=self.fonts["subtitle"],
            bg=self.colors["light"],
            fg=self.colors["secondary"],
            padx=20,
            pady=20
        )
        lot_frame.pack(fill=tk.BOTH, expand=True)

        self.parking_canvas = tk.Canvas(
            lot_frame,
            bg="white",
            highlightthickness=0
        )
        self.parking_canvas.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        legend_frame = tk.Frame(lot_frame, bg=self.colors["light"])
        legend_frame.pack(fill=tk.X, pady=(10, 0))

        legend_items = [
            ("Empty Slot", self.colors["empty_slot"]),
            ("Car", "#3498db"),
            ("Bike", "#e74c3c"),
            ("Truck", "#f39c12"),
            ("SUV", "#9b59b6")
        ]

        for text, color in legend_items:
            item_frame = tk.Frame(legend_frame, bg=self.colors["light"])
            item_frame.pack(side=tk.LEFT, padx=10)

            color_box = tk.Label(
                item_frame,
                bg=color,
                width=3,
                height=1,
                relief=tk.SUNKEN,
                bd=1
            )
            color_box.pack(side=tk.LEFT, padx=(0, 5))

            text_label = tk.Label(
                item_frame,
                text=text,
                font=self.fonts["small"],
                bg=self.colors["light"],
                fg=self.colors["dark"]
            )
            text_label.pack(side=tk.LEFT)

        self.draw_parking_lot()

    def draw_parking_lot(self):
        """Draw the parking lot visualization"""
        self.parking_canvas.delete("all")

        canvas_width = self.parking_canvas.winfo_width()
        canvas_height = self.parking_canvas.winfo_height()

        if canvas_width < 100 or canvas_height < 100:
            canvas_width = 600
            canvas_height = 400

        rows = 3
        cols = 4
        slot_width = canvas_width // (cols + 2)
        slot_height = canvas_height // (rows + 2)

        for row in range(rows):
            for col in range(cols):
                slot_num = row * cols + col + 1
                x1 = (col + 1) * slot_width
                y1 = (row + 1) * slot_height
                x2 = x1 + slot_width - 10
                y2 = y1 + slot_height - 10

                vehicle = self.parking_lot.get_slot_status(slot_num)

                if vehicle:
                    color = vehicle.color
                    self.parking_canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=color,
                        outline=self.colors["slot_border"],
                        width=2
                    )

                    self.parking_canvas.create_text(
                        x1 + (x2 - x1) // 2,
                        y1 + 20,
                        text=f"Slot {slot_num}",
                        font=("Segoe UI", 10, "bold"),
                        fill="white"
                    )

                    self.parking_canvas.create_text(
                        x1 + (x2 - x1) // 2,
                        y1 + 40,
                        text=vehicle.vehicle_type.value[:3],
                        font=("Segoe UI", 10, "bold"),
                        fill="white"
                    )

                    self.parking_canvas.create_text(
                        x1 + (x2 - x1) // 2,
                        y2 - 15,
                        text=vehicle.vehicle_id,
                        font=("Segoe UI", 8),
                        fill="white"
                    )
                else:
                    self.parking_canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=self.colors["empty_slot"],
                        outline=self.colors["slot_border"],
                        width=2,
                        dash=(5, 5)
                    )

                    self.parking_canvas.create_text(
                        x1 + (x2 - x1) // 2,
                        y1 + (y2 - y1) // 2,
                        text=f"Slot {slot_num}\nEMPTY",
                        font=("Segoe UI", 10),
                        fill=self.colors["dark"],
                        justify=tk.CENTER
                    )

        self.parking_canvas.create_text(
            canvas_width // 2,
            20,
            text="ENTRY/EXIT",
            font=("Segoe UI", 12, "bold"),
            fill=self.colors["primary"]
        )

        self.parking_canvas.create_rectangle(
            20, 40, canvas_width - 20, canvas_height - 20,
            outline=self.colors["dark"],
            width=3
        )

    def create_vehicle_controls(self, parent):
        """Create vehicle parking/removal controls"""
        controls_frame = tk.LabelFrame(
            parent,
            text="Vehicle Management",
            font=self.fonts["subtitle"],
            bg=self.colors["light"],
            fg=self.colors["secondary"],
            padx=20,
            pady=20
        )
        controls_frame.pack(fill=tk.X, pady=(0, 20))

        notebook = ttk.Notebook(controls_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        park_frame = tk.Frame(notebook, bg=self.colors["light"])
        notebook.add(park_frame, text="Park Vehicle")
        self.create_park_controls(park_frame)

        remove_frame = tk.Frame(notebook, bg=self.colors["light"])
        notebook.add(remove_frame, text="Remove Vehicle")
        self.create_remove_controls(remove_frame)

        quick_frame = tk.Frame(notebook, bg=self.colors["light"])
        notebook.add(quick_frame, text="Quick Actions")
        self.create_quick_controls(quick_frame)

    def create_park_controls(self, parent):
        """Create controls for parking vehicles"""
        type_frame = tk.Frame(parent, bg=self.colors["light"])
        type_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            type_frame,
            text="Vehicle Type:",
            font=self.fonts["normal"],
            bg=self.colors["light"],
            fg=self.colors["dark"],
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT)

        self.vehicle_type_var = tk.StringVar(value=VehicleType.CAR.value)
        type_combo = ttk.Combobox(
            type_frame,
            textvariable=self.vehicle_type_var,
            values=[v.value for v in VehicleType],
            state="readonly",
            width=15
        )
        type_combo.pack(side=tk.LEFT, padx=(10, 0))

        id_frame = tk.Frame(parent, bg=self.colors["light"])
        id_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            id_frame,
            text="Vehicle ID:",
            font=self.fonts["normal"],
            bg=self.colors["light"],
            fg=self.colors["dark"],
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT)

        self.vehicle_id_entry = tk.Entry(
            id_frame,
            font=self.fonts["normal"],
            width=20
        )
        self.vehicle_id_entry.pack(side=tk.LEFT, padx=(10, 0))

        random_id_btn = tk.Button(
            id_frame,
            text="Random",
            command=self.generate_random_id,
            font=("Segoe UI", 10),
            bg=self.colors["warning"],
            fg="white",
            width=8
        )
        random_id_btn.pack(side=tk.LEFT, padx=(5, 0))

        owner_frame = tk.Frame(parent, bg=self.colors["light"])
        owner_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            owner_frame,
            text="Owner Name:",
            font=self.fonts["normal"],
            bg=self.colors["light"],
            fg=self.colors["dark"],
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT)

        self.owner_name_entry = tk.Entry(
            owner_frame,
            font=self.fonts["normal"],
            width=20
        )
        self.owner_name_entry.pack(side=tk.LEFT, padx=(10, 0))

        park_button = tk.Button(
            parent,
            text="Park Vehicle",
            command=self.park_vehicle,
            font=("Segoe UI", 14, "bold"),
            bg=self.colors["success"],
            fg="white",
            activebackground=self.colors["success"],
            activeforeground="white",
            relief=tk.RAISED,
            bd=3,
            padx=20,
            pady=10
        )
        park_button.pack(fill=tk.X, pady=(20, 10))

        self.park_status_label = tk.Label(
            parent,
            text="Enter vehicle details to park",
            font=self.fonts["small"],
            bg=self.colors["light"],
            fg=self.colors["dark"],
            wraplength=300
        )
        self.park_status_label.pack(pady=(0, 10))

    def create_remove_controls(self, parent):
        """Create controls for removing vehicles"""
        id_frame = tk.Frame(parent, bg=self.colors["light"])
        id_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            id_frame,
            text="Vehicle ID to remove:",
            font=self.fonts["normal"],
            bg=self.colors["light"],
            fg=self.colors["dark"],
            width=20,
            anchor="w"
        ).pack(side=tk.LEFT)

        self.remove_id_entry = tk.Entry(
            id_frame,
            font=self.fonts["normal"],
            width=20
        )
        self.remove_id_entry.pack(side=tk.LEFT, padx=(10, 0))

        slot_frame = tk.Frame(parent, bg=self.colors["light"])
        slot_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            slot_frame,
            text="Or select slot:",
            font=self.fonts["normal"],
            bg=self.colors["light"],
            fg=self.colors["dark"],
            width=20,
            anchor="w"
        ).pack(side=tk.LEFT)

        self.slot_var = tk.StringVar()
        slot_combo = ttk.Combobox(
            slot_frame,
            textvariable=self.slot_var,
            values=[str(i) for i in range(1,
                                          self.parking_lot.capacity + 1)],
            state="readonly",
            width=10
        )
        slot_combo.pack(side=tk.LEFT, padx=(10, 0))
        slot_combo.bind("<<ComboboxSelected>>", self.on_slot_selected)

        remove_button = tk.Button(
            parent,
            text="Remove Vehicle",
            command=self.remove_vehicle,
            font=("Segoe UI", 14, "bold"),
            bg=self.colors["danger"],
            fg="white",
            activebackground=self.colors["danger"],
            activeforeground="white",
            relief=tk.RAISED,
            bd=3,
            padx=20,
            pady=10
        )
        remove_button.pack(fill=tk.X, pady=(20, 10))

        self.remove_status_label = tk.Label(
            parent,
            text="Enter vehicle ID or select slot to remove",
            font=self.fonts["small"],
            bg=self.colors["light"],
            fg=self.colors["dark"],
            wraplength=300
        )
        self.remove_status_label.pack(pady=(0, 10))

        self.fee_label = tk.Label(
            parent,
            text="",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors["light"],
            fg=self.colors["primary"]
        )
        self.fee_label.pack()

    def create_quick_controls(self, parent):
        """Create quick action controls"""
        quick_park_frame = tk.Frame(parent, bg=self.colors["light"])
        quick_park_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            quick_park_frame,
            text="Quick Park:",
            font=self.fonts["normal"],
            bg=self.colors["light"],
            fg=self.colors["dark"],
            anchor="w"
        ).pack(fill=tk.X, pady=(0, 5))

        vehicle_types = [
            ("Car", VehicleType.CAR, self.colors["primary"]),
            ("Bike", VehicleType.BIKE, self.colors["danger"]),
            ("Truck", VehicleType.TRUCK, self.colors["warning"]),
            ("SUV", VehicleType.SUV, self.colors["info"])
        ]

        for text, v_type, color in vehicle_types:
            btn = tk.Button(
                quick_park_frame,
                text=text,
                command=lambda vt=v_type: self.quick_park(vt),
                font=self.fonts["normal"],
                bg=color,
                fg="white",
                activebackground=color,
                activeforeground="white",
                relief=tk.RAISED,
                bd=2,
                padx=10,
                pady=5
            )
            btn.pack(side=tk.LEFT, padx=2)

        emergency_frame = tk.Frame(parent, bg=self.colors["light"])
        emergency_frame.pack(fill=tk.X, pady=(20, 10))

        emergency_btn = tk.Button(
            emergency_frame,
            text="Emergency Clear All",
            command=self.emergency_clear,
            font=self.fonts["normal"],
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            relief=tk.RAISED,
            bd=2,
            padx=20,
            pady=8
        )
        emergency_btn.pack(fill=tk.X)

        reset_frame = tk.Frame(parent, bg=self.colors["light"])
        reset_frame.pack(fill=tk.X, pady=(10, 0))

        reset_btn = tk.Button(
            reset_frame,
            text="Reset Parking Lot",
            command=self.reset_parking_lot,
            font=self.fonts["normal"],
            bg="#95a5a6",
            fg="white",
            activebackground="#7f8c8d",
            activeforeground="white",
            relief=tk.RAISED,
            bd=2,
            padx=20,
            pady=8
        )
        reset_btn.pack(fill=tk.X)

    def create_parking_stats(self, parent):
        """Create parking statistics panel"""
        stats_frame = tk.LabelFrame(
            parent,
            text="Parking Statistics",
            font=self.fonts["subtitle"],
            bg=self.colors["light"],
            fg=self.colors["secondary"],
            padx=20,
            pady=20
        )
        stats_frame.pack(fill=tk.X, pady=(0, 20))

        stats_grid = tk.Frame(stats_frame, bg=self.colors["light"])
        stats_grid.pack(fill=tk.BOTH, expand=True)

        self.create_stat_box(stats_grid, 0, 0, "Total Capacity",
                             str(self.parking_lot.capacity),
                             self.colors["primary"])

        self.available_slots_var = tk.StringVar(value="12")
        self.create_stat_box(stats_grid, 0, 1, "Available Slots", "12",
                             self.colors["success"],
                             var=self.available_slots_var)

        self.occupied_slots_var = tk.StringVar(value="0")
        self.create_stat_box(stats_grid, 1, 0, "Occupied Slots", "0",
                             self.colors["danger"],
                             var=self.occupied_slots_var)

        self.occupancy_var = tk.StringVar(value="0%")
        self.create_stat_box(stats_grid, 1, 1, "Occupancy Rate", "0%",
                             self.colors["warning"],
                             var=self.occupancy_var)

        self.revenue_var = tk.StringVar(value="$0.00")
        self.create_stat_box(stats_grid, 2, 0, "Total Revenue", "$0.00",
                             self.colors["info"],
                             var=self.revenue_var)

        self.total_vehicles_var = tk.StringVar(value="0")
        self.create_stat_box(stats_grid, 2, 1, "Total Parked", "0",
                             self.colors["secondary"],
                             var=self.total_vehicles_var)

        for i in range(3):
            stats_grid.grid_rowconfigure(i, weight=1)
        for j in range(2):
            stats_grid.grid_columnconfigure(j, weight=1)

    def create_stat_box(self, parent, row, col, title, value, color,
                        var=None):
        """Create a statistic box"""
        box_frame = tk.Frame(parent, bg=self.colors["light"],
                             relief=tk.RAISED, bd=2)
        box_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        title_label = tk.Label(
            box_frame,
            text=title,
            font=self.fonts["small"],
            bg=color,
            fg="white",
            pady=5
        )
        title_label.pack(fill=tk.X)

        if var:
            value_label = tk.Label(
                box_frame,
                textvariable=var,
                font=("Segoe UI", 20, "bold"),
                bg=self.colors["light"],
                fg=color,
                pady=10
            )
        else:
            value_label = tk.Label(
                box_frame,
                text=value,
                font=("Segoe UI", 20, "bold"),
                bg=self.colors["light"],
                fg=color,
                pady=10
            )
        value_label.pack(expand=True, fill=tk.BOTH)

    def create_vehicle_list(self, parent):
        """Create list of parked vehicles"""
        list_frame = tk.LabelFrame(
            parent,
            text="Currently Parked Vehicles",
            font=self.fonts["subtitle"],
            bg=self.colors["light"],
            fg=self.colors["secondary"],
            padx=20,
            pady=20
        )
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("slot", "id", "type", "owner", "entry_time")
        self.vehicles_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            height=8
        )

        self.vehicles_tree.heading("slot", text="Slot")
        self.vehicles_tree.heading("id", text="Vehicle ID")
        self.vehicles_tree.heading("type", text="Type")
        self.vehicles_tree.heading("owner", text="Owner")
        self.vehicles_tree.heading("entry_time", text="Entry Time")

        self.vehicles_tree.column("slot", width=60, anchor=tk.CENTER)
        self.vehicles_tree.column("id", width=100, anchor=tk.W)
        self.vehicles_tree.column("type", width=80, anchor=tk.CENTER)
        self.vehicles_tree.column("owner", width=120, anchor=tk.W)
        self.vehicles_tree.column("entry_time", width=100, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                  command=self.vehicles_tree.yview)
        self.vehicles_tree.configure(yscrollcommand=scrollbar.set)

        self.vehicles_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def initialize_demo_vehicles(self):
        """Initialize with some parked vehicles for demonstration"""
        demo_vehicles = [
            ("ABC123", VehicleType.CAR, "John Smith"),
            ("XYZ789", VehicleType.BIKE, "Alice Johnson"),
            ("TRK456", VehicleType.TRUCK, "Bob Wilson"),
            ("SUV321", VehicleType.SUV, "Carol Davis")
        ]

        for vehicle_id, vehicle_type, owner in demo_vehicles:
            if vehicle_type == VehicleType.CAR:
                vehicle = Car(vehicle_id, owner)
            elif vehicle_type == VehicleType.BIKE:
                vehicle = Bike(vehicle_id, owner)
            elif vehicle_type == VehicleType.TRUCK:
                vehicle = Truck(vehicle_id, owner)
            elif vehicle_type == VehicleType.SUV:
                vehicle = SUV(vehicle_id, owner)

            try:
                self.parking_lot.park_vehicle(vehicle)
            except ParkingLotFullError:
                break

        self.update_display()

    def update_real_time_info(self):
        """Update real-time information"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"{current_time}")

        if self.parking_lot.is_full():
            status = "FULL"
            status_color = "#e74c3c"
        elif self.parking_lot.is_empty():
            status = "EMPTY"
            status_color = "#2ecc71"
        else:
            occupied = self.parking_lot.get_total_vehicles_parked()
            status = f"{occupied}/{self.parking_lot.capacity}"
            status_color = "#f39c12"

        self.status_label.config(text=status, fg=status_color)

        self.root.after(1000, self.update_real_time_info)

    def generate_random_id(self):
        """Generate random vehicle ID"""
        letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
        numbers = ''.join(random.choices('0123456789', k=3))
        vehicle_id = f"{letters}{numbers}"
        self.vehicle_id_entry.delete(0, tk.END)
        self.vehicle_id_entry.insert(0, vehicle_id)

        first_names = ["John", "Jane", "Robert", "Emily", "Michael",
                       "Sarah", "David", "Lisa"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones",
                      "Garcia", "Miller", "Davis"]
        owner = f"{random.choice(first_names)} {random.choice(last_names)}"
        self.owner_name_entry.delete(0, tk.END)
        self.owner_name_entry.insert(0, owner)

    def park_vehicle(self):
        """Park a vehicle in the parking lot"""
        vehicle_id = self.vehicle_id_entry.get().strip().upper()
        owner_name = self.owner_name_entry.get().strip()
        vehicle_type_str = self.vehicle_type_var.get()

        if not vehicle_id:
            self.park_status_label.config(
                text="Please enter a vehicle ID",
                fg=self.colors["danger"]
            )
            return

        if not owner_name:
            owner_name = "Unknown"

        if vehicle_id in self.parking_lot.vehicles:
            self.park_status_label.config(
                text=f"Vehicle {vehicle_id} is already parked!",
                fg=self.colors["danger"]
            )
            return

        vehicle_type = VehicleType(vehicle_type_str)
        if vehicle_type == VehicleType.CAR:
            vehicle = Car(vehicle_id, owner_name)
        elif vehicle_type == VehicleType.BIKE:
            vehicle = Bike(vehicle_id, owner_name)
        elif vehicle_type == VehicleType.TRUCK:
            vehicle = Truck(vehicle_id, owner_name)
        elif vehicle_type == VehicleType.SUV:
            vehicle = SUV(vehicle_id, owner_name)

        try:
            slot_number = self.parking_lot.park_vehicle(vehicle)

            self.update_display()

            self.park_status_label.config(
                text=f"Vehicle {vehicle_id} parked in Slot {slot_number}",
                fg=self.colors["success"]
            )

            self.vehicle_id_entry.delete(0, tk.END)
            self.owner_name_entry.delete(0, tk.END)

            self.animate_parking(slot_number)

        except ParkingLotFullError as error_msg:
            self.park_status_label.config(
                text=f"No available slots!",
                fg=self.colors["danger"]
            )

    def animate_parking(self, slot_number):
        """Animate parking action"""
        canvas_width = self.parking_canvas.winfo_width()
        canvas_height = self.parking_canvas.winfo_height()

        if canvas_width > 100:
            rows = 3
            cols = 4
            slot_width = canvas_width // (cols + 2)
            slot_height = canvas_height // (rows + 2)

            row = (slot_number - 1) // cols
            col = (slot_number - 1) % cols

            x = (col + 1) * slot_width + slot_width // 2
            y = (row + 1) * slot_height + slot_height // 2

            highlight = self.parking_canvas.create_oval(
                x-20, y-20, x+20, y+20,
                fill="yellow",
                outline="orange",
                width=3
            )

            for _ in range(3):
                self.parking_canvas.itemconfig(highlight, fill="yellow")
                self.root.update()
                time.sleep(0.1)
                self.parking_canvas.itemconfig(highlight, fill="orange")
                self.root.update()
                time.sleep(0.1)

            self.parking_canvas.delete(highlight)

    def on_slot_selected(self, event):
        """When a slot is selected in the combo box"""
        slot_str = self.slot_var.get()
        if slot_str:
            slot_num = int(slot_str)
            vehicle = self.parking_lot.get_slot_status(slot_num)
            if vehicle:
                self.remove_id_entry.delete(0, tk.END)
                self.remove_id_entry.insert(0, vehicle.vehicle_id)
                self.remove_status_label.config(
                    text=f"Found: {vehicle.vehicle_id} "
                         f"({vehicle.vehicle_type.value})",
                    fg=self.colors["info"]
                )
            else:
                self.remove_status_label.config(
                    text=f"Slot {slot_num} is empty",
                    fg=self.colors["warning"]
                )

    def remove_vehicle(self):
        """Remove a vehicle from the parking lot"""
        vehicle_id = self.remove_id_entry.get().strip().upper()

        if not vehicle_id:
            self.remove_status_label.config(
                text="Please enter a vehicle ID",
                fg=self.colors["danger"]
            )
            return

        try:
            vehicle, fee = self.parking_lot.remove_vehicle(vehicle_id)

            self.update_display()

            self.remove_status_label.config(
                text=f"Vehicle {vehicle_id} removed",
                fg=self.colors["success"]
            )

            self.fee_label.config(
                text=f"Parking Fee: ${fee:.2f}",
                fg=self.colors["primary"]
            )

            self.show_receipt(vehicle, fee)

            self.remove_id_entry.delete(0, tk.END)
            self.slot_var.set("")

        except ValueError as error_msg:
            self.remove_status_label.config(
                text=f"{str(error_msg)}",
                fg=self.colors["danger"]
            )
            self.fee_label.config(text="")

    def show_receipt(self, vehicle, fee):
        """Show parking receipt"""
        receipt_window = tk.Toplevel(self.root)
        receipt_window.title("Parking Receipt")
        receipt_window.geometry("400x300")
        receipt_window.configure(bg=self.colors["light"])
        receipt_window.transient(self.root)

        receipt_window.update_idletasks()
        x = (self.root.winfo_x() + (self.root.winfo_width() // 2) - 200)
        y = (self.root.winfo_y() + (self.root.winfo_height() // 2) - 150)
        receipt_window.geometry(f"+{x}+{y}")

        content_frame = tk.Frame(receipt_window, bg=self.colors["light"],
                                 padx=30, pady=30)
        content_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            content_frame,
            text="PARKING RECEIPT",
            font=("Segoe UI", 20, "bold"),
            bg=self.colors["light"],
            fg=self.colors["primary"]
        ).pack(pady=(0, 20))

        details = [
            f"Vehicle ID: {vehicle.vehicle_id}",
            f"Vehicle Type: {vehicle.vehicle_type.value}",
            f"Owner: {vehicle.owner_name}",
            f"Slot: {vehicle.slot_number}",
            f"Entry Time: {vehicle.entry_time.strftime('%H:%M:%S') if vehicle.entry_time else 'N/A'}",
            f"Exit Time: {datetime.now().strftime('%H:%M:%S')}",
            "",
            f"Parking Fee: ${fee:.2f}",
            "Thank you for parking with us!"
        ]

        for detail in details:
            tk.Label(
                content_frame,
                text=detail,
                font=self.fonts["normal"],
                bg=self.colors["light"],
                fg=self.colors["dark"]
            ).pack(anchor="w", pady=2)

        tk.Button(
            content_frame,
            text="Close",
            command=receipt_window.destroy,
            font=self.fonts["normal"],
            bg=self.colors["primary"],
            fg="white",
            padx=20,
            pady=8
        ).pack(pady=(20, 0))

    def quick_park(self, vehicle_type):
        """Quick park a random vehicle"""
        letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
        numbers = ''.join(random.choices('0123456789', k=3))
        vehicle_id = f"{letters}{numbers}"

        first_names = ["John", "Jane", "Robert", "Emily", "Michael",
                       "Sarah", "David", "Lisa"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones",
                      "Garcia", "Miller", "Davis"]
        owner = f"{random.choice(first_names)} {random.choice(last_names)}"

        if vehicle_type == VehicleType.CAR:
            vehicle = Car(vehicle_id, owner)
        elif vehicle_type == VehicleType.BIKE:
            vehicle = Bike(vehicle_id, owner)
        elif vehicle_type == VehicleType.TRUCK:
            vehicle = Truck(vehicle_id, owner)
        elif vehicle_type == VehicleType.SUV:
            vehicle = SUV(vehicle_id, owner)

        try:
            slot_number = self.parking_lot.park_vehicle(vehicle)

            self.update_display()

            messagebox.showinfo(
                "Quick Park",
                f"{vehicle_type.value} {vehicle_id} parked in Slot "
                f"{slot_number}"
            )

        except ParkingLotFullError:
            messagebox.showwarning(
                "Parking Lot Full",
                "Parking lot is full! Cannot park more vehicles."
            )

    def emergency_clear(self):
        """Emergency clear all vehicles"""
        if self.parking_lot.is_empty():
            messagebox.showinfo("Empty", "Parking lot is already empty.")
            return

        response = messagebox.askyesno(
            "Emergency Clear",
            "EMERGENCY CLEAR ALL VEHICLES!\n\n"
            "This will remove ALL vehicles from the parking lot.\n"
            "Parking fees will NOT be collected.\n\n"
            "Are you sure you want to continue?"
        )

        if response:
            while self.parking_lot.vehicles:
                vehicle_id = list(self.parking_lot.vehicles.keys())[0]
                try:
                    self.parking_lot.remove_vehicle(vehicle_id)
                except Exception:
                    pass

            self.update_display()

            messagebox.showinfo(
                "Cleared",
                "All vehicles have been cleared from the parking lot."
            )

    def reset_parking_lot(self):
        """Reset the parking lot (new day)"""
        response = messagebox.askyesno(
            "Reset Parking Lot",
            "Reset the parking lot for a new day?\n\n"
            "This will clear all vehicles and reset statistics."
        )

        if response:
            self.parking_lot.reset()
            self.update_display()
            messagebox.showinfo("Reset",
                                "Parking lot has been reset.")

    def update_display(self):
        """Update all display elements"""
        self.draw_parking_lot()

        available = len(self.parking_lot.get_available_slots())
        occupied = len(self.parking_lot.get_occupied_slots())
        occupancy_rate = self.parking_lot.get_occupancy_rate()

        self.available_slots_var.set(str(available))
        self.occupied_slots_var.set(str(occupied))
        self.occupancy_var.set(f"{occupancy_rate:.1f}%")
        self.revenue_var.set(f"${self.parking_lot.revenue:.2f}")
        self.total_vehicles_var.set(str(self.parking_lot.total_vehicles))

        for item in self.vehicles_tree.get_children():
            self.vehicles_tree.delete(item)

        for vehicle in self.parking_lot.vehicles.values():
            vehicle_data = vehicle.to_dict()
            self.vehicles_tree.insert(
                "", tk.END,
                values=(
                    vehicle_data["slot"],
                    vehicle_data["id"],
                    vehicle_data["type"],
                    vehicle_data["owner"],
                    vehicle_data["entry_time"]
                )
            )

def main():
    """Main function to run the application"""
    root = tk.Tk()
    AutomatedParkingLotSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()
