안녕하세요 조교님,
readme 를 읽어주셔서 감사합니다.
아래 내용은 부팅 할 때에 나오는 메시지와 같습니다.
참고 해주시면 감사하겠습니다.

##1. sqldeveloper setting##
Before executing this program,
you must set your sqldevelop setting as below.
In SqlDeveloper preferences:
Tools > Preferences > Database > Worksheet,
check the option for "New Worksheet to use unshared connction"
(한국어"도구>환경설정>워크시트>공유되지 않은 접속을 사용할 새 워크시트)

If not, update may not presume and just hang, due to oracle bug.
(Refer to https://stackoverflow.com/a/42420331)

##2. Initialize DB##
Please initialize all the DB information
exactly like the given createschema.sql file.

Please double check before evaluation.

Press Enter if you checked this content. Thank you.
