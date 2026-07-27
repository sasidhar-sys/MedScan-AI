"""Initial PocketScan-AI schema

Revision ID: f5fc5f5a33d9
Revises: 
Create Date: 2026-07-27 10:13:13.436736

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f5fc5f5a33d9'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('full_name', sa.String(length=150), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'DOCTOR', 'RESEARCHER', name='userrole'), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. doctors
    op.create_table(
        'doctors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('medical_license_number', sa.String(length=100), nullable=False),
        sa.Column('specialization', sa.String(length=150), nullable=False),
        sa.Column('hospital_name', sa.String(length=255), nullable=False),
        sa.Column('department', sa.String(length=150), nullable=True),
        sa.Column('years_of_experience', sa.Integer(), nullable=False),
        sa.Column('qualification', sa.String(length=255), nullable=True),
        sa.Column('profile_photo', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_doctors_medical_license_number'), 'doctors', ['medical_license_number'], unique=True)

    # 3. patients
    op.create_table(
        'patients',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('doctor_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('patient_id', sa.String(length=50), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('gender', sa.Enum('MALE', 'FEMALE', 'OTHER', name='gender'), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('blood_group', sa.String(length=5), nullable=True),
        sa.Column('emergency_contact_name', sa.String(length=150), nullable=True),
        sa.Column('emergency_contact_phone', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_patients_doctor_id'), 'patients', ['doctor_id'], unique=False)
    op.create_index(op.f('ix_patients_patient_id'), 'patients', ['patient_id'], unique=True)

    # 4. clinical_histories
    op.create_table(
        'clinical_histories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chief_complaint', sa.Text(), nullable=True),
        sa.Column('symptoms', sa.Text(), nullable=True),
        sa.Column('medical_history', sa.Text(), nullable=True),
        sa.Column('surgical_history', sa.Text(), nullable=True),
        sa.Column('family_history', sa.Text(), nullable=True),
        sa.Column('allergies', sa.Text(), nullable=True),
        sa.Column('current_medications', sa.Text(), nullable=True),
        sa.Column('smoking_history', sa.Boolean(), nullable=False),
        sa.Column('alcohol_history', sa.Boolean(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        sa.UniqueConstraint('patient_id')
    )
    op.create_index(op.f('ix_clinical_histories_patient_id'), 'clinical_histories', ['patient_id'], unique=True)

    # 5. uploaded_images
    op.create_table(
        'uploaded_images',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('modality', sa.Enum('ENDOSCOPY', 'BIOPSY', 'CT', 'MRI', 'PET_CT', name='imagemodality'), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('stored_filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('upload_status', sa.Enum('UPLOADED', 'PROCESSING', 'COMPLETED', 'FAILED', name='uploadstatus'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        sa.UniqueConstraint('stored_filename')
    )
    op.create_index(op.f('ix_uploaded_images_patient_id'), 'uploaded_images', ['patient_id'], unique=False)

    # 6. predictions
    op.create_table(
        'predictions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('uploaded_image_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('predicted_class', sa.String(length=100), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('risk_level', sa.Enum('LOW', 'MEDIUM', 'HIGH', name='risklevel'), nullable=False),
        sa.Column('model_name', sa.String(length=150), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('inference_time_ms', sa.Integer(), nullable=True),
        sa.Column('gradcam_path', sa.String(length=500), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('prediction_status', sa.Enum('PENDING', 'COMPLETED', 'FAILED', name='predictionstatus'), nullable=False),
        sa.ForeignKeyConstraint(['uploaded_image_id'], ['uploaded_images.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_predictions_uploaded_image_id'), 'predictions', ['uploaded_image_id'], unique=False)

    # 7. ai_reports
    op.create_table(
        'ai_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('prediction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('report_title', sa.String(length=255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('findings', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('disclaimer', sa.Text(), nullable=False),
        sa.Column('report_pdf_path', sa.String(length=500), nullable=True),
        sa.Column('report_status', sa.Enum('DRAFT', 'FINALIZED', 'ARCHIVED', name='reportstatus'), nullable=False),
        sa.ForeignKeyConstraint(['prediction_id'], ['predictions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        sa.UniqueConstraint('prediction_id')
    )
    op.create_index(op.f('ix_ai_reports_prediction_id'), 'ai_reports', ['prediction_id'], unique=True)

    # 8. audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.Enum('LOGIN', 'LOGOUT', 'CREATE', 'UPDATE', 'DELETE', 'VIEW', 'UPLOAD', 'AI_PREDICTION', 'REPORT_GENERATED', name='auditaction'), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_resource_id'), 'audit_logs', ['resource_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_resource_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_table('audit_logs')

    op.drop_index(op.f('ix_ai_reports_prediction_id'), table_name='ai_reports')
    op.drop_table('ai_reports')

    op.drop_index(op.f('ix_predictions_uploaded_image_id'), table_name='predictions')
    op.drop_table('predictions')

    op.drop_index(op.f('ix_uploaded_images_patient_id'), table_name='uploaded_images')
    op.drop_table('uploaded_images')

    op.drop_index(op.f('ix_clinical_histories_patient_id'), table_name='clinical_histories')
    op.drop_table('clinical_histories')

    op.drop_index(op.f('ix_patients_patient_id'), table_name='patients')
    op.drop_index(op.f('ix_patients_doctor_id'), table_name='patients')
    op.drop_table('patients')

    op.drop_index(op.f('ix_doctors_medical_license_number'), table_name='doctors')
    op.drop_table('doctors')

    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
