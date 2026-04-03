import os
import time
import random
import string

def create_mock_file(path, content, age_days):
    with open(path, "w") as f:
        f.write(content)
    # Modify access and modification times
    current_time = time.time()
    past_time = current_time - (age_days * 24 * 3600)
    os.utime(path, (past_time, past_time))

def generate_enterprise_dataset(base_dir):
    print(f"Generating simulated Microsoft Enterprise Dataset in: {base_dir}")
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # Scenarios:
    # 1. Telemetry Logs: Huge, often outdated, redundant over time.
    # 2. Duplicate Binaries/Installers: Copied across different user profiles.
    # 3. Active Project Source Code: Small, frequently accessed.
    
    # 1. Telemetry Logs (Old and Large -> Should be flagged as Redundant)
    telemetry_dir = os.path.join(base_dir, "telemetry_logs")
    os.makedirs(telemetry_dir, exist_ok=True)
    for i in range(1, 11):
        content = "USER_TELEMETRY_DATA: " + "".join(random.choices(string.ascii_letters, k=1024*500)) # 500 KB per log
        # 80% of logs are older than 200 days
        age = random.choice([250, 300, 400, 10, 5])
        create_mock_file(os.path.join(telemetry_dir, f"win11_telemetry_{i}.log"), content, age)

    # 2. Duplicate Installers (Same Content -> Deduplication)
    installer_dir = os.path.join(base_dir, "software_distributions")
    os.makedirs(installer_dir, exist_ok=True)
    installer_content = "MS_OFFICE_INSTALLER_BINARY_MOCK_" + "".join(random.choices(string.ascii_letters, k=1024*1024)) # 1 MB
    create_mock_file(os.path.join(installer_dir, "Office365_Setup_DepartmentA.exe"), installer_content, 10)
    create_mock_file(os.path.join(installer_dir, "Office365_Setup_DepartmentB.exe"), installer_content, 12)
    create_mock_file(os.path.join(installer_dir, "Office365_Setup_IT.exe"), installer_content, 5)

    # 3. Active Projects (New, accessed recently -> Important)
    project_dir = os.path.join(base_dir, "active_projects", "Azure_Core")
    os.makedirs(project_dir, exist_ok=True)
    for i in range(1, 6):
        content = "def azure_cloud_function():\n\treturn 'Operational'\n"
        create_mock_file(os.path.join(project_dir, f"cloud_module_{i}.py"), content, random.randint(1, 15))

    print("Dataset generation complete.")

if __name__ == "__main__":
    generate_enterprise_dataset("./ms_enterprise_data")
