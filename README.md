GITHUB ACTIONS POC - EMPLOYEE FINFER

Keyless auth from Github Actions:
https://cloud.google.com/blog/products/identity-security/enabling-keyless-authentication-from-github-actions

https://medium.com/google-cloud/keyless-authentication-to-google-cloud-from-github-actions-with-workload-identity-federation-605e725b51d

https://gcloud.devoteam.com/blog/keyless-authentication-using-github-actions-and-google-cloud/

https://www.youtube.com/watch?v=XPjxOvUj0BA

Found GitHub actions for CI/CD tasks:

Git Check Out:
https://github.com/marketplace/actions/checkout
Checkout  - uses: 'actions/checkout@v4'

GCP Auth  - 
https://github.com/marketplace/actions/authenticate-to-google-cloud
uses: 'google-github-actions/auth@v1'

GCP Deploy to Cloud Functions - 
https://github.com/marketplace/actions/cloud-functions-deploy
uses: 'google-github-actions/deploy-cloud-functions@v1'

Sonarqube: 
https://github.com/marketplace/actions/official-sonarqube-scan
uses sonarsource/sonarqube-scan-action@master

checkMarx: 
https://github.com/checkmarx-ts/checkmarx-github-action
uses checkmarx-ts/checkmarx-github-action@<version> 

42chrunch:
https://github.com/marketplace/actions/42crunch-rest-api-static-security-testing
uses 42Crunch/api-security-audit-action@v3


WIF Creation for Github actions Auth:
To create WIF Pool:
gcloud iam workload-identity-pools create "git-action-pool" --project="employee-finder-407218" --location="global" --display-name="git action pool"

To create WIF Provider:
gcloud iam workload-identity-pools providers create-oidc "git-action-provider" --project="employee-finder-407218" --location="global" --workload-identity-pool="git-action-pool" --display-name="git-action-provider" --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.aud=assertion.aud" --issuer-uri="https://token.actions.githubusercontent.com"

IAM Binding of Github Repository to WIF Binding:
gcloud iam service-accounts add-iam-policy-binding "github-deployer@employee-finder-407218.iam.gserviceaccount.com" --project="employee-finder-407218" --role="roles/iam.workloadIdentityUser" --member="principalSet://iam.googleapis.com/projects/104429179211/locations/global/workloadIdentityPools/git-action-pool/attribute.repository/Chippu1987/Helloworld" 

Workflow file:
```
name: Deploy Cloud Functions
on:
  push:
    branches:
      - main

permissions:
  contents: 'read'
  id-token: write

jobs:
  GithubAction-Cloud_Function-Deployment:
    runs-on: ubuntu-latest
    steps:
    - id: 'auth'
      name: 'Authenticate to GCP'
      uses: 'google-github-actions/auth@v0.3.1'
      with:
          create_credentials_file: 'true'
          workload_identity_provider: ${{ secrets.WORKLOAD_IDENTITY_PROVIDER }}
          service_account: ${{ secrets.SERVICE_ACCOUNT }}

    - id: 'gcloud'
      name: 'List the Services Enabled in the Project'
      run: |-
        gcloud auth login --brief --cred-file="${{ steps.auth.outputs.credentials_file_path }}"
        gcloud services list --project ${{ secrets.GCP_PROJECT_ID }}
    - id: 'GIT-Checkout'
      name: 'Checkout the Source Code'
      uses: actions/checkout@v2

    - id: 'Install-python-package'
      name : 'Install Packages'
      run : |-
        sudo apt install python3
    
    - id: 'run-python-test'
      name : 'Executing Unit Test Cases'
      run : |-
        python3 test.py
    - id: 'deploy'
      name: 'Deploy the Python Source Code to GCP Cloud Fucntion'
      uses: 'google-github-actions/deploy-cloud-functions@v1'
      with:
        name: 'glcoud-wif-cloud-function'
        runtime: 'python312'
        entry_point: hello_world
        project_id: ${{ secrets.GCP_PROJECT_ID }}

    - id: 'Set_IAM_Policy_Binding'
      name: 'Set IAM Policy binding to allow unauthenticated user access'
      run: |-
        gcloud functions add-iam-policy-binding glcoud-wif-cloud-function \
        --member="allUsers" \
        --role="roles/cloudfunctions.invoker" \
        --project ${{ secrets.GCP_PROJECT_ID }}
    - id: 'Test_Cloud_Function_Endpoint'
      name: 'Test the Cloud Function endpoint'
      run: |-
        curl https://us-central1-employee-finder-407218.cloudfunctions.net/glcoud-wif-cloud-function
```
