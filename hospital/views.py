from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from .models import Doctor, Patient, Appoinment

# Create your views here.
def About(request):
    return render(request,'about.html')

def Home(request):
    return render(request,'home.html')

def Contact(request):
    return render(request,'contact.html')

def Index(request):
    if not request.user.is_staff:
        return redirect('login')
    return render(request, 'index.html')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('uname')  # This line retrieves the value of the 'uname' field from the POST data submitted in the form.
        password = request.POST.get('pwd')  # This line retrieves the value of the 'pwd' field from the POST data submitted in the form.

        user = authenticate(request, username=username, password=password) # This line uses the authenticate function to check if the provided username and password match any user in the database. If a valid user is found, the user variable will contain the corresponding user object; otherwise, it will be None.
        if user is not None and user.is_staff: # This line checks whether the user variable is not None (i.e., a valid user object) and whether the user has the is_staff attribute set to True. The is_staff attribute is typically used to designate admin users in Django's default user model.
            login(request, user) # This line uses the login function to log in the user. It creates a user session and associates it with the current request.
            return redirect('dashboard')  # Replace 'admin_home' with the URL name of your admin dashboard/homepage
        else:
            error_message = "Invalid credentials or insufficient permissions. Please try again."
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def admin_logout(request):
    logout(request)
    return redirect('admin_login')  # Redirect to the admin login page after logout

def add_doctor(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        special = request.POST.get('special')
        Doctor.objects.create(Name=name, Phone=phone, Special=special)
        return redirect('view_doctor')
    return render(request, 'add_doctor.html')

def View_doctor(request):
    if not request.user.is_staff:
        return redirect('login')
    doc = Doctor.objects.all()
    d={'doc':doc}
    return render(request,'view_doctor.html',d)

def Delete_doctor(request, pid):
    if not request.user.is_staff:
        return redirect('login')
    doctor = Doctor.objects.get(id=pid)
    doctor.delete()
    return redirect('view_doctor')

def add_patient(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        age = request.POST.get('age')
        address = request.POST.get('address')
        Patient.objects.create(Name=name, Gender=gender, Age=age, Address=address)
        return redirect('view_patient')
    return render(request, 'add_patient.html')

def view_patient(request):
    if not request.user.is_staff:
        return redirect('login')
    patients = Patient.objects.all()
    return render(request, 'view_patient.html', {'patients': patients})

def delete_patient(request, patient_id):
    if not request.user.is_staff:
        return redirect('login')
    patient = Patient.objects.get(id=patient_id)
    patient.delete()
    return redirect('view_patient')

def add_appointment(request):
    doctors = Doctor.objects.all()
    patients = Patient.objects.all()

    if not doctors.exists() or not patients.exists():
        if not doctors.exists() and not patients.exists():
            messages.warning(request, "Aucun médecin ni patient n'est disponible pour le moment. Veuillez d'abord enregistrer ces informations.")
        elif not doctors.exists():
            messages.warning(request, "Aucun médecin n'est disponible pour le moment. Veuillez ajouter un médecin avant de demander un rendez-vous.")
        else:
            messages.warning(request, "Aucun patient n'est disponible pour le moment. Veuillez ajouter un patient avant de demander un rendez-vous.")

    if request.method == 'POST':
        if not doctors.exists() or not patients.exists():
            messages.error(request, "La demande de rendez-vous est impossible tant que les médecins et les patients n'ont pas été enregistrés.")
            return render(request, 'add_appointment.html', {'doctors': doctors, 'patients': patients})

        doctor_id = request.POST.get('doctor')
        patient_id = request.POST.get('patient')
        date = request.POST.get('date')
        time = request.POST.get('time')

        if not doctor_id or not patient_id or not date or not time:
            messages.error(request, "Merci de remplir tous les champs du formulaire de rendez-vous.")
            return render(request, 'add_appointment.html', {'doctors': doctors, 'patients': patients})

        doctor = Doctor.objects.get(pk=doctor_id)
        patient = Patient.objects.get(pk=patient_id)

        slot_taken = Appoinment.objects.filter(Doctor=doctor, date=date, time=time).exists()
        if slot_taken:
            messages.error(request, "Ce médecin est déjà réservé à cette date et à cette heure. Merci de choisir un autre créneau.")
            return render(request, 'add_appointment.html', {'doctors': doctors, 'patients': patients})

        Appoinment.objects.create(Doctor=doctor, Patient=patient, date=date, time=time)
        messages.success(request, "Le rendez-vous a bien été enregistré.")
        return redirect('add_appointment')

    return render(request, 'add_appointment.html', {'doctors': doctors, 'patients': patients})

def view_appointment(request):
    if not request.user.is_staff:
        return redirect('login')
    appointments = Appoinment.objects.all()
    return render(request, 'view_appointment.html', {'appointments': appointments})



def delete_appointment(request, appointment_id):
    if not request.user.is_staff:
        return redirect('login')
    appointment = Appoinment.objects.get(id=appointment_id)
    appointment.delete()
    return redirect('view_appointment')

def dashboard(request):
    total_doctors = Doctor.objects.count()
    total_patients = Patient.objects.count()
    total_appointments = Appoinment.objects.count()
    return render(request, 'dashboard.html', {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
    })
