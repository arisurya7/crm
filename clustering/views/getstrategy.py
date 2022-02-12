from django.http.response import JsonResponse

def getstrategy(request):
    data = checkStrategyFM(request.GET.get('code_strategy'))
    data = {
        'data':data
    }
    return JsonResponse(data)

def checkStrategyFM(type_rfm):
    if type_rfm == 'F↑M↑':
        return {
            'name' : 'Enforced Strategy (F↑ M↑)',
            'strategy' : [
                'Menjaga komunikasi dengan pelanggan.',
                'Menjaga interaktif jangka panjang.',
                'Merancang program loyalitas pelanggan.',
                'Mengerti kebutuhan dan kebiasaan pelanggan.'
            ],

            'saran' : [
                'Mengirim informasi promosi melalui telepon, fax dan email.',
                'Memberikan diskon pada acara tertentu.',
                'Melakukan wawancara dengan pelanggan mengenai penawaran produk melalui telepon.'
            ]
        }
    
    elif type_rfm == 'F↑M↓':
        return {
            'name' : 'Offensive Strategy (F↑ M↓)',
            'strategy' : [
               'Mempertahankan loyalitas pelanggan dengan kegiatan up-selling dan cross-selling',
               'Mempertahankan loyalitas dengan pelanggan.',
               'Mengembangkan kegiatan promosi untuk meningkatkan frekuensi',
               'Menarik minat pelanggan dengan produk atau layanan baru.'
            ],

            'saran' : [
                'Mempromosikan produk baru atau produk pelengkap.',
                'Meningkatkan pembelian pelanggan dengan menawarkan produk yang paling banyak dibeli.' 
            ]
        }
    
    elif type_rfm == 'F↓M↑':
        return  {
            'name' : 'Defensive Strategy (F↓ M↑)',
            'strategy' : [
                'Mengembangkan kegiatan promosi untuk meningkatkan frekuensi.',
                'Mengirim informasi produk/layanan secara berkala.'               
            ],

            'saran' : [
                'Merancang layanan purna jual.',
                'Menawarkan produk up-selling dengan harga khusus.'
            ]
        }

    elif type_rfm == 'F↓M↓':
        return  {
            'name' : 'Let-go Strategy (F↓ M↓)',
            'strategy' : [
               'Tidak ada keharusan perusahaan untuk memperhatikan segmen ini.',
               'Memilih produk dengan fokus utama yang dibutuhkan pelanggan.',
            ],

            'saran' : [
                'Memisahkan pelanggan baru dan pelanggan lama.',
                'Melakukan komunikasi hanya dengan pelanggan baru.'
            ]
        }
    else:
        return'kosong'