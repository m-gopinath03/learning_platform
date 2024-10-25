from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

class NotificationManager:
    @staticmethod
    def send_new_content_notification(content, student):
        subject = f'New Content Added: {content.course.title}'
        context = {
            'student_name': student.get_full_name() or student.username,
            'course_title': content.course.title,
            'content_title': content.title,
            'instructor_name': content.course.instructor.get_full_name()
        }
        
        html_message = render_to_string('emails/new_content_notification.html', context)
        plain_message = render_to_string('emails/new_content_notification.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email],
            fail_silently=True
        )
    
    @staticmethod
    def send_new_course_notification(course, student):
        subject = f'New Course by {course.instructor.get_full_name()}'
        context = {
            'student_name': student.get_full_name() or student.username,
            'course_title': course.title,
            'instructor_name': course.instructor.get_full_name(),
            'course_description': course.description
        }
        
        html_message = render_to_string('emails/new_course_notification.html', context)
        plain_message = render_to_string('emails/new_course_notification.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email],
            fail_silently=True
        )
