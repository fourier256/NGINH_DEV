; cellType에 해당하는 모든 인스턴스를 하위까지 찾아 full name으로 출력
(procedure (findHierInstByCellType cv cellType path
  )
  (foreach inst cv~>instances
    (let ((curPath (strcat path "/" inst~>name)))
      (if (equal (inst~>master~>cellName) cellType)
        (printf "%s/%s/%s/%s\n" inst~>libName inst~>cellName inst~>viewName curPath)
        )
      ; 아래에서 recursion으로 하위 hierarchy 진입
      (let ((subCv (dbOpenCellViewByType inst~>libName inst~>cellName inst~>viewName "" "r")))
        (when subCv
          (findHierInstByCellType subCv cellType curPath)
          (dbClose subCv)
        )
      )
    )
  )
)
; 사용 예
(let ((cv (geGetWindowCellView)))
  (findHierInstByCellType cv "nmos1v" "")
)
