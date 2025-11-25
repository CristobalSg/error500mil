from __future__ import annotations

import subprocess
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, status
from pydantic import BaseModel

from app.fet.results_parser import TimetableResultsParser
from app.fet.schemas import FetRunRequest, FetRunSummary
from app.fet.xml_builder import FetXmlBuilder
from app.settings import AppSettings


class FetRunResult(BaseModel):
    input_file: str
    output_directory: str
    stdout: str = ""
    stderr: str = ""
    return_code: int


class FetService:
    """
    Servicio principal que recibe un payload de datos ya consolidados, genera el archivo .fet,
    ejecuta FET y devuelve un resumen de la corrida.
    """

    def __init__(
        self,
        settings: AppSettings,
        xml_builder: FetXmlBuilder | None = None,
        results_parser: TimetableResultsParser | None = None,
    ):
        self.settings = settings
        self.xml_builder = xml_builder or FetXmlBuilder()
        self.results_parser = results_parser or TimetableResultsParser()

    def run(self, payload: FetRunRequest) -> FetRunSummary:
        fet_xml = self.xml_builder.build(payload)
        input_file = self._write_input_file(fet_xml)
        execution = self._execute_algorithm(input_file)
        metadata = payload.metadata
        activities_schedule, rooms = self.results_parser.extract_summary(
            payload=payload,
            workdir=self.settings.fet_workdir,
            input_file=input_file,
        )
        return FetRunSummary(
            semester=metadata.semester,
            timetable_id=metadata.timetable_id,
            fet_input_file=execution.input_file,
            output_directory=execution.output_directory,
            stdout=execution.stdout,
            stderr=execution.stderr,
            activities_schedule=activities_schedule,
            rooms=rooms,
        )

    def _write_input_file(self, xml_payload: str) -> Path:
        workdir = self.settings.fet_workdir
        workdir.mkdir(parents=True, exist_ok=True)
        file_path = workdir / f"fet-input-{uuid4().hex}.fet"
        file_path.write_text(xml_payload, encoding="utf-8")
        return file_path

    def _execute_algorithm(self, input_file: Path) -> FetRunResult:
        binary = self.settings.fet_binary_path
        if not binary.exists():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"No se encontró el binario de FET en {binary}",
            )

        try:
            completed = subprocess.run(
                [
                    str(binary),
                    f"--inputfile={input_file}",
                    f"--outputdir={self.settings.fet_workdir}",
                ],
                capture_output=True,
                text=True,
                cwd=binary.parent,
                timeout=self.settings.fet_timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:  # noqa: F841
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="La ejecución de FET superó el tiempo máximo permitido",
            ) from None
        except FileNotFoundError as exc:  # noqa: F841
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo ejecutar el binario de FET",
            ) from None

        if completed.returncode != 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="FET finalizó con errores",
            )

        return FetRunResult(
            input_file=str(input_file),
            output_directory=str(self.settings.fet_workdir),
            stdout=completed.stdout,
            stderr=completed.stderr,
            return_code=completed.returncode,
        )


__all__ = ["FetService", "FetRunRequest", "FetRunSummary", "FetRunResult"]
