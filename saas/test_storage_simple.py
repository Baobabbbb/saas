import asyncio
import sys
import os
import tempfile
sys.path.append('.')

async def test_storage():
    try:
        from services.supabase_storage import get_storage_service

        service = get_storage_service()
        if not service:
            print('❌ Service Supabase Storage non initialise')
            return

        print('✅ Service Supabase Storage initialise')

        # Tester avec un fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('Test de stockage Supabase')
            test_file = f.name

        try:
            result = service.upload_file(
                file_path=test_file,
                user_id='test_user',
                content_type='audio',
                custom_filename='test_storage.txt'
            )

            print(f'Resultat upload: {result}')

            if result['success']:
                print(f'✅ Upload reussi: {result["signed_url"][:80]}...')
            else:
                print(f'❌ Upload echoue: {result.get("error", "Erreur inconnue")}')

        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)

    except Exception as e:
        print(f'❌ Erreur test: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_storage())




































