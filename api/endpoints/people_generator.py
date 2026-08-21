# api/endpoints/people_generator.py — Эндпоинты генерации людей, семей, организаций

import logging
from fastapi import HTTPException

from api.schemas import (
    GeneratePersonRequest,
    GenerateFamilyRequest,
    GenerateOrganizationRequest,
    GenerateCountryRequest,
    GenerateWorldPopulationRequest,
    WorldAddPeopleRequest,
)

logger = logging.getLogger("people_generator")


async def generate_person(req: GeneratePersonRequest) -> dict:
    """POST /generate/person — Сгенерировать человека."""
    try:
        from utils.world_people_generator import PeopleGenerator
        generator = PeopleGenerator()
        person = generator.generate_person(
            age_range=(req.age_min, req.age_max), gender=req.gender, archetype=req.archetype
        )
        return {"status": "ok", "person": person.to_dict()}
    except Exception as e:
        logger.error(f"❌ Ошибка генерации человека: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def generate_family(req: GenerateFamilyRequest) -> dict:
    """POST /generate/family — Сгенерировать семью."""
    try:
        from utils.world_people_generator import PeopleGenerator
        generator = PeopleGenerator()
        family = generator.generate_family(size=req.size, region=req.region)
        return {"status": "ok", "family": family.to_dict()}
    except Exception as e:
        logger.error(f"❌ Ошибка генерации семьи: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def generate_organization(req: GenerateOrganizationRequest) -> dict:
    """POST /generate/organization — Сгенерировать организацию."""
    try:
        from utils.world_people_generator import PeopleGenerator
        generator = PeopleGenerator()
        organization = generator.generate_organization(type=req.type, size=req.size)
        return {"status": "ok", "organization": organization.to_dict()}
    except Exception as e:
        logger.error(f"❌ Ошибка генерации организации: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def generate_country(req: GenerateCountryRequest) -> dict:
    """POST /generate/country — Сгенерировать страну."""
    try:
        from utils.world_people_generator import PeopleGenerator
        generator = PeopleGenerator()
        country = generator.generate_country(population_range=(req.population_min, req.population_max))
        return {"status": "ok", "country": country.to_dict()}
    except Exception as e:
        logger.error(f"❌ Ошибка генерации страны: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def generate_world_population(req: GenerateWorldPopulationRequest) -> dict:
    """POST /generate/world-population — Сгенерировать популяцию мира."""
    try:
        from utils.world_people_generator import PeopleGenerator
        generator = PeopleGenerator()
        world_data = generator.generate_world_population(
            num_people=req.people, num_families=req.families,
            num_organizations=req.organizations, num_countries=req.countries
        )
        return {"status": "ok", "stats": world_data["stats"], "output_file": "data/generated_worlds/world_population_*.json"}
    except Exception as e:
        logger.error(f"❌ Ошибка генерации популяции: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def world_add_people(world_name: str, req: WorldAddPeopleRequest) -> dict:
    """POST /world/{world_name}/add-people — Добавить людей в мир."""
    try:
        from utils.world_people_generator import WorldEngineIntegration
        integration = WorldEngineIntegration()
        success = integration.add_people_to_world(world_name, num_people=req.num)

        if success:
            return {"status": "ok", "detail": f"Добавлено {req.num} персонажей в мир {world_name}"}
        raise HTTPException(status_code=404, detail=f"Мир {world_name} не найден")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка добавления людей в мир: {e}")
        raise HTTPException(status_code=500, detail=str(e))
