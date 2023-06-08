# Müzik Çalar Kullanım Kılavuzu

Bu, FastAPI ve Selenium ile oluşturulmuş bir müzik çalar uygulaması için Python kodudur. Uygulama, kullanıcılara bir YouTube çalma listesinden müzik çalmalarına ve sonraki çalınacak şarkılara oy vermelerine olanak tanır.

## Önkoşullar

Uygulamayı çalıştırmadan önce aşağıdaki bağımlılıkların yüklü olduğundan emin olun:

-   Python (3.7 veya üzeri)
-   FastAPI
-   Selenium
-   Pytube
-   Uvicorn
-   Firefox tarayıcısı
-   Geckodriver

Python bağımlılıklarını pip kullanarak yükleyebilirsiniz:

`pip install fastapi selenium pytube uvicorn` 

Ayrıca Geckodriver yürütülebilir dosyasını ve Firefox tarayıcısını indirmeniz gerekmektedir. Geckodriver, Selenium tarafından kullanılan Firefox tarayıcısı için sürücüdür. Geckodriver yürütülebilir dosyasını resmi Mozilla deposundan indirebilirsiniz: [https://github.com/mozilla/geckodriver/releases](https://github.com/mozilla/geckodriver/releases)

Geckodriver yürütülebilir dosyasını Python kod dosyasının bulunduğu dizine yerleştirmeyi unutmayın.

## Uygulamayı Çalıştırma

Müzik çalar uygulamasını çalıştırmak için aşağıdaki adımları izleyin:

1.  Bir terminal veya komut istemi açın.
2.  Python kod dosyasının bulunduğu dizine gidin.
3.  Aşağıdaki komutu çalıştırın:

`uvicorn main:app --reload` 

4.  Uygulama çalışmaya başlayacak ve terminalde "Hello World" mesajını göreceksiniz.
5.  Web tarayıcısı veya Postman gibi bir API test aracı kullanarak uygulamanın API uç noktalarına erişebilirsiniz.

## API Uç Noktaları

Müzik çalar uygulaması aşağıdaki API uç noktalarını sağlar:

-   `GET /`: "Hello World" mesajını içeren bir JSON yanıtı döndürür.
-   `GET /track/current`: Şu anda çalan müzik hakkında bilgileri, URL, başlık, süre, sanatçı ve küçük resim gibi, döndürür.
-   `GET /vote/song`: Oy kullanılabilecek olası sonraki şarkıların bir listesini döndürür. Her şarkı, URL, başlık, süre, sanatçı ve küçük resim içerir.
-   `POST /vote/song`: Belirli bir şarkıya oy vermek için şarkı URL'sini istek gövdesinde belirtir.
-   `DELETE /vote/song`: Belirli bir şarkı için oy kullanmayı kaldırmak için şarkı URL'sini istek gövdesinde belirtir.

## Kod Yapısı

Kod, birkaç sınıfa bölünmüştür:

-   `Music`: URL, başlık, süre, sanatçı ve küçük resim gibi özellikleri olan bir müzik parçasını temsil eder. Nesneyi JSON formatına dönüştürmek için `toJson` metodunu sağlar.
-   `Playlist`: Müzik parçalarının bir çalma listesini temsil eder. YouTube çalma listesi URL'sini giriş olarak alır ve Pytube kullanarak videoların listesini alır. Videolar `Music` nesnelerine dönüştürülür ve karıştırılır.
-   `Player`: Müzik çalar işlevselliğini yönetir. Firefox tarayıcısı ve reklam engelleme eklentisi ile Selenium WebDriver'ı başlatır. Ayrıca çalma listesini, çalınan parçaların listesini ve oy listesini başlatır. `play` yöntemi belirli bir müzik parçasını çalar ve oy sayısına göre çalınacak sonraki şarkıyı seçme mantığını yönetir.
-   `FastAPI`: FastAPI uygulamasını başlatır, `Player` örneği oluşturur ve arka planda `player.play(player.playlist.videos[0])` işlemini başlatır.