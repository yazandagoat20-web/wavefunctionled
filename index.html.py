import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

# Material database: { Name: Bandgap in eV }
MATERIALS = {
    "Gallium Nitride (GaN) - UV": 3.40,
    "Indium Gallium Nitride (InGaN) - Blue": 2.80,
    "Indium Gallium Nitride (InGaN) - Green": 2.40,
    "Gallium Arsenide Phosphide (GaAsP) - Yellow": 2.10,
    "Aluminum Gallium Arsenide (AlGaAs) - Red": 1.85,
    "Gallium Arsenide (GaAs) - Infrared": 1.42
}

def wl_to_rgb(wavelength):
    """Approximates an RGB color from a wavelength in nanometers."""
    wl = int(wavelength)
    if 380 <= wl < 440:
        R, G, B = -(wl - 440) / (440 - 380), 0.0, 1.0
    elif 440 <= wl < 490:
        R, G, B = 0.0, (wl - 440) / (490 - 440), 1.0
    elif 490 <= wl < 510:
        R, G, B = 0.0, 1.0, -(wl - 510) / (510 - 490)
    elif 510 <= wl < 580:
        R, G, B = (wl - 510) / (580 - 510), 1.0, 0.0
    elif 580 <= wl < 645:
        R, G, B = 1.0, -(wl - 645) / (645 - 580), 0.0
    elif 645 <= wl <= 780:
        R, G, B = 1.0, 0.0, 0.0
    else:
        R, G, B = 0.3, 0.3, 0.3
        
    factor = 1.0 if 420 <= wl <= 700 else (0.3 + 0.7 * (wl - 380) / (420 - 380) if wl < 420 else 0.3 + 0.7 * (780 - wl) / (780 - 700))
    return f'#{int(R*factor*255):02x}{int(G*factor*255):02x}{int(B*factor*255):02x}'

def update_ui_elements():
    """Updates static text readouts and background colors when material changes."""
    material_name = material_var.get()
    Eg = MATERIALS[material_name]
    wavelength = 1240.0 / Eg
    
    bg_label.config(text=f"Band Gap Energy (Eg): {Eg:.2f} eV")
    wl_label.config(text=f"Peak Wavelength (λ): {wavelength:.1f} nm")
    
    led_color = wl_to_rgb(wavelength)
    led_bulb.config(bg=led_color)

def animate_wave(frame):
    """The continuous animation loop producing a true propagating light wave."""
    material_name = material_var.get()
    Eg = MATERIALS[material_name]
    wavelength = 1240.0 / Eg
    
    x = np.linspace(300, 900, 1000)
    
    # 1. Physics: The Gaussian Envelope (determines WHERE the light is localized)
    sigma = 40  # Width of the wave packet
    envelope = np.exp(-0.5 * ((x - wavelength) / sigma) ** 2)
    
    # 2. Physics: Traveling Wave Propagation (sin(kx - wt))
    # Wave number (k) scales inversely with the actual physical wavelength
    k = 2.0 * np.pi / (wavelength * 0.1) 
    omega_t = frame * 0.4  # Time evolution phase velocity shift
    
    # Generate the actual crests and troughs moving across the spatial coordinate
    traveling_wave = np.sin(k * x - omega_t)
    
    # Combine envelope and oscillation, shifted up to fit neatly on a 0 to 1 scale
    y_propagating = envelope * (0.5 + 0.5 * traveling_wave)
    
    led_color = wl_to_rgb(wavelength)
    plot_color = led_color if led_color != '#1e1e1e' else 'purple'
    
    # Instantly update the rendering data stream
    line.set_data(x, y_propagating)
    
    global current_fill
    if 'current_fill' in globals() and current_fill:
        current_fill.remove()
    current_fill = ax.fill_between(x, y_propagating, color=plot_color, alpha=0.25)
    
    return line, current_fill

# --- Build UI App Frame Interface ---
root = tk.Tk()
root.title("Real Traveling Wave LED Simulator")
root.geometry("800x500")
root.configure(bg="#2d2d2d")

panel_frame = tk.Frame(root, bg="#2d2d2d", width=300)
panel_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)

tk.Label(panel_frame, text="Select Substrate Material:", bg="#2d2d2d", fg="white", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5)

material_keys = list(MATERIALS.keys())
material_var = tk.StringVar(value=material_keys[0])

dropdown = ttk.Combobox(panel_frame, textvariable=material_var, values=material_keys, state="readonly", width=35)
dropdown.pack(fill=tk.X, pady=5)
material_var.trace_add("write", lambda *args: update_ui_elements())

bg_label = tk.Label(panel_frame, text="", bg="#2d2d2d", fg="#00ffcc", font=("Arial", 11))
bg_label.pack(anchor=tk.W, pady=10)

wl_label = tk.Label(panel_frame, text="", bg="#2d2d2d", fg="#ffcc00", font=("Arial", 11))
wl_label.pack(anchor=tk.W, pady=5)

tk.Label(panel_frame, text="Simulated LED Die:", bg="#2d2d2d", fg="white", font=("Arial", 10)).pack(anchor=tk.W, pady=15)
led_bulb = tk.Label(panel_frame, width=12, height=4, bd=3, relief=tk.RIDGE)
led_bulb.pack(pady=5)

# Right Graphics Plot Visualization Node Panel layout configuration
plot_frame = tk.Frame(root, bg="#1e1e1e")
plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
fig.patch.set_facecolor('#1e1e1e')

ax.set_title("Traveling Wave Packet Propagation", color='white', fontsize=12)
ax.set_xlabel("Wavelength Spectrum Position (nm)", color='white')
ax.set_ylabel("Electric Field Amplitude", color='white')
ax.set_facecolor('#1e1e1e')
ax.tick_params(colors='white')
ax.set_xlim(300, 900)
ax.set_ylim(-0.05, 1.1)

line, = ax.plot([], [], linewidth=2.5)
current_fill = None

canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

update_ui_elements()

# Launch high-framerate animation loop (15ms interval for continuous wave motion)
ani = animation.FuncAnimation(fig, animate_wave, frames=200, interval=15, blit=False)

root.mainloop()
