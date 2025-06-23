from django.core.management.base import BaseCommand
from myapp.models import Video
from django.db.models import Count

class Command(BaseCommand):
    help = 'Remove duplicate videos based on URL'

    def handle(self, *args, **options):
        # Find videos with duplicate URLs
        duplicates = Video.objects.values('url').annotate(count=Count('id')).filter(count__gt=1)
        
        for duplicate in duplicates:
            url = duplicate['url']
            videos = Video.objects.filter(url=url).order_by('id')
            
            # Keep the first video (oldest) and delete the rest
            first_video = videos.first()
            videos.exclude(id=first_video.id).delete()
            
            self.stdout.write(
                self.style.SUCCESS(f'Kept video ID {first_video.id} and removed duplicates with URL: {url}')
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully removed duplicate videos'))
