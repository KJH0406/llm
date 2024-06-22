# Memory

    메모리는 각 예시 내용만 파악

- **ConversationBufferMemory**
  - 메모리에 모든 대화 기록을 다 저장하기 때문에 대화가 길어지면 길어질 수록 메모리에 수 많은 내용이 쌓이게 됨.
- **ConversationBufferWindowMemory**
  - 특정 부분만 메모리에 저장하여 더 효율적으로 구성할 수 있게끔 하는 것임.
  - 예를 들어 최근 5개의 메시지까지만 저장하고 나머지 가장 오래된 메시지들은 삭제되는 것.
- **ConversationSummaryMemory**
  - 대화 내용을 계속해서 요약해서 생성해 나가는거라서 많은 토큰과 시간이 들음.
  - 하지만 대화가 진행되면 진행될수록 계속해서 내용이 많아지고 쓰면쓸수록 효율적이게 됨.
- **ConversationSummaryBufferMemory**
  - 위 두가지를 합친 버전
  - 일정 메시지 개수를 초과하면 그전까지있었던 것은 삭제하는 것이 아닌 요약해서 저장함.
  - 아마 위 두가지를 사용하는 것보단 이게 가장 효율적일듯?
- **ConversationKGMemory**
  - 대화 도중에 중요한 정보를 추출해서 저장 그리고 Knowledge graph에서 히스토리를 가져오는 것이 아닌 엔티티를 가져옴.
